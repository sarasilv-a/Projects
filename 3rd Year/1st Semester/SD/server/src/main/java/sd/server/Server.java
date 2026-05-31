package sd.server;

import sd.common.*;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import java.util.concurrent.atomic.AtomicInteger;

public class Server {

    private volatile boolean running;
    private Thread clientConnectionHandler;
    private Thread serverWorker;
    private final AuthenticationService authService;
    private final MyThreadSafeQueue<ConnectionManager.Packet> requestQueue;
    private final MyThreadSafeMap<String, byte[]> keyValueStore;
    private final MyThreadSafeMap<Integer, MyThreadSafeQueue<ConnectionManager.Packet>> responseQueues;
    private final MyThreadSafeMap<String, LockConditionPair> conditionMap;
    private final MyThreadSafeMap<String, byte[]> valueConditionMap;
    private final MyThreadSafePool threadPool;
    private final Lock clientSlotLock;
    private final Condition clientSlotAvailable;
    private final int maxConcurrentClients;
    private final AtomicInteger currentClientCount;

    private static final int BATCH_SIZE = 10;

    public Server(int maxConcurrentClients, int maxConcurrentThreads) {
        this.running = false;
        this.authService = new AuthenticationService();
        this.requestQueue = new MyThreadSafeQueue<>();
        this.keyValueStore = new MyThreadSafeMap<>();
        this.responseQueues = new MyThreadSafeMap<>();
        this.conditionMap = new MyThreadSafeMap<>();
        this.valueConditionMap = new MyThreadSafeMap<>();
        this.threadPool = new MyThreadSafePool(maxConcurrentThreads);
        this.clientSlotLock = new ReentrantLock();
        this.clientSlotAvailable = clientSlotLock.newCondition();
        this.maxConcurrentClients = maxConcurrentClients;
        this.currentClientCount = new AtomicInteger(0);
    }

    public void run(int clientPort) {
        shutDownHookThread();
        this.running = true;

        this.clientConnectionHandler = new Thread(() -> runClientConnectionHandler(clientPort));
        this.clientConnectionHandler.start();

        this.serverWorker = new Thread(this::runServerWorker);
        this.serverWorker.start();
    }

    public void runClientConnectionHandler(int clientPort) {
        try (ServerSocket serverSocket = new ServerSocket(clientPort)) {
            logInfo("Waiting for client connections on port " + clientPort);

            while (this.running) {
                try {
                    Socket clientSocket = serverSocket.accept();
                    // Wait for a slot to be available if max concurrent clients reached
                    if (currentClientCount.incrementAndGet() > maxConcurrentClients) {
                        clientSlotLock.lock();
                        try {
                            while (currentClientCount.get() > maxConcurrentClients) {
                                logInfo("Max concurrent clients reached. Waiting for a slot to be available...");
                                clientSlotAvailable.await();
                            }
                        } finally {
                            clientSlotLock.unlock();
                        }
                    }
                    logInfo("Client connected: " + clientSocket.getInetAddress().getHostAddress());

                    new Thread(() -> {
                        try {
                            handleClient(clientSocket);
                        } finally {
                            clientSlotLock.lock();
                            try {
                                currentClientCount.decrementAndGet();
                                clientSlotAvailable.signal();
                                logInfo("Client disconnected. Slot available for new connections.");
                            } finally {
                                clientSlotLock.unlock();
                            }
                        }
                    }).start();
                } catch (IOException e) {
                    if (this.running) {
                        logError("Error accepting client connection: " + e.getMessage());
                    }
                } catch (InterruptedException e) {
                    logError("Interrupted while waiting for a client slot: " + e.getMessage());
                    Thread.currentThread().interrupt();
                }
            }
        } catch (IOException e) {
            logError("Error starting client handler: " + e.getMessage());
        }
    }

    private void handleClient(Socket clientSocket) {
        try (ConnectionManager connectionManager = new ConnectionManager(clientSocket)) {
            boolean authenticated = false;
            int authUserId = -1;

            // Authenticate user
            while (!authenticated) {
                ConnectionManager.Packet authPacket = connectionManager.receivePacket();
                if (authPacket.getMessage() instanceof AuthRequest authRequest) {
                    logInfo("Authentication request received for user: " + authRequest.getUsername());

                    authUserId = authService.authenticateUser(authRequest);
                    connectionManager.send(authPacket.getTag(), new AuthResponse(authUserId));

                    if (authUserId > 0) {
                        authenticated = true;
                        logInfo("User authenticated successfully: UserID " + authUserId);
                    } else {
                        logInfo("Authentication failed for user: " + authRequest.getUsername());
                    }
                } else {
                    logWarning("Invalid message type received during authentication.");
                }
            }

            int userId = authUserId;
            // Start a new thread to handle client responses
            new Thread(() -> handleClientResponses(connectionManager, userId)).start();

            // Handle client requests
            while (this.running) {
                ConnectionManager.Packet request = connectionManager.receivePacket();
                if (request != null) {
                    requestQueue.add(request);
                    logInfo("Request added to queue from UserID " + userId + ": " + request.getMessage());
                }
            }
        } catch (Exception e) {
            logError("Error handling client: " + e.getMessage());
        }
    }

    private void handleClientResponses(ConnectionManager connectionManager, int userId) {
        MyThreadSafeQueue<ConnectionManager.Packet> clientQueue = responseQueues.get(userId);

        // Create a new response queue if not present
        if (clientQueue == null) {
            clientQueue = new MyThreadSafeQueue<>();
            responseQueues.put(userId, clientQueue);
        }

        // Send responses to client
        while (this.running) {
            ConnectionManager.Packet response = clientQueue.poll();
            if (response != null) {
                logInfo("Sending response to UserID " + userId + ": " + response.getMessage());
                try {
                    connectionManager.send(response.getTag(), response.getMessage());
                } catch (IOException e) {
                    logError("Error sending response to client UserID " + userId + ": " + e.getMessage());
                }
            }
        }
    }

    private void runServerWorker() {
        while (this.running) {
            List<ConnectionManager.Packet> batch = new ArrayList<>();

            // Get requests in batch
            for (int i = 0; i < BATCH_SIZE; i++) {
                ConnectionManager.Packet request = requestQueue.poll();
                if (request == null) break;
                batch.add(request);
            }

            // Process requests in batch
            for (ConnectionManager.Packet request : batch) {
                // Process request in a separate thread from the thread pool
                threadPool.submit(() -> {
                    logInfo("Processing request from queue: " + request.getMessage());
                    Message responseMessage;

                    switch (request.getMessage()) {
                        case PutRequest putRequest -> {
                            keyValueStore.put(putRequest.getKey(), putRequest.getValue());
                            responseMessage = new PutResponse(putRequest.getClientID(), true);
                            logInfo("PutRequest processed successfully for UserID " + putRequest.getClientID() + " with key: " + putRequest.getKey());
                        }
                        case GetRequest getRequest -> {
                            byte[] value = keyValueStore.get(getRequest.getKey());
                            if (value != null) {
                                responseMessage = new GetResponse(getRequest.getClientID(), value);
                                logInfo("GetRequest processed successfully for UserID " + getRequest.getClientID() + " with key: " + getRequest.getKey());
                            } else {
                                responseMessage = new GetResponse(getRequest.getClientID(), new byte[0]);
                                logInfo("GetRequest processed for UserID " + getRequest.getClientID() + " with key: " + getRequest.getKey() + " - Key not found.");
                            }
                        }
                        case MultiPutRequest multiPutRequest -> {
                            Map<String, byte[]> pairs = multiPutRequest.getPairs();
                            for (Map.Entry<String, byte[]> entry : pairs.entrySet()) {
                                keyValueStore.put(entry.getKey(), entry.getValue());
                            }
                            responseMessage = new MultiPutResponse(multiPutRequest.getClientID(), true);
                            logInfo("MultiPutRequest processed successfully for UserID " + multiPutRequest.getClientID() + " with keys: " + pairs.keySet());
                        }
                        case MultiGetRequest multiGetRequest -> {
                            Set<String> keys = multiGetRequest.getKeys();
                            Map<String, byte[]> foundPairs = new HashMap<>();
                            for (String key : keys) {
                                byte[] value = keyValueStore.get(key);
                                if (value != null) {
                                    foundPairs.put(key, value);
                                }
                            }
                            responseMessage = new MultiGetResponse(multiGetRequest.getClientID(), foundPairs);
                            logInfo("MultiGetRequest processed successfully for UserID " + multiGetRequest.getClientID() + " with keys: " + keys);
                        }
                        case GetWhenRequest getWhenRequest -> {
                            String key = getWhenRequest.getKey();
                            String conditionKey = getWhenRequest.getKeyCond();
                            byte[] conditionValue = getWhenRequest.getValueCond();

                            // Pair Condition with Lock
                            LockConditionPair pair = conditionMap.computeIfAbsent(conditionKey, k -> new LockConditionPair());
                            pair.lock();
                            try {
                                while (!matchesCondition(conditionKey, conditionValue)) {
                                    logInfo("GetWhenRequest for key " + key + " is waiting for condition on " + conditionKey);
                                    try {
                                        pair.await();
                                    } catch (InterruptedException e) {
                                        throw new RuntimeException(e);
                                    }
                                }

                                byte[] value = keyValueStore.get(key);
                                responseMessage = new GetResponse(getWhenRequest.getClientID(), value);
                                logInfo("GetWhenRequest processed successfully for key: " + key + ", UserID: " + getWhenRequest.getClientID());
                            } finally {
                                pair.unlock();
                            }
                        }
                        case PutConditionRequest putConditionRequest -> {
                            String key = putConditionRequest.getKey();
                            byte[] value = putConditionRequest.getValue();

                            LockConditionPair pair = conditionMap.get(key);
                            if (pair != null) {
                                pair.lock();
                                try {
                                    valueConditionMap.put(key, value);
                                    pair.signalAll();
                                    logInfo("Signaled all threads waiting on condition for key: " + key);
                                } finally {
                                    pair.unlock();
                                }
                            } else {
                                valueConditionMap.put(key, value);
                            }
                            responseMessage = new PutResponse(putConditionRequest.getClientID(), true);
                            logInfo("PutConditionRequest processed successfully for key: " + key + ", UserID: " + putConditionRequest.getClientID());
                        }

                        default -> throw new IllegalStateException("Unexpected value: " + request.getMessage());
                    }

                    // Add response to client-specific queue
                    MyThreadSafeQueue<ConnectionManager.Packet> clientQueue = responseQueues.get(responseMessage.getClientID());
                    if (clientQueue == null) {
                        clientQueue = new MyThreadSafeQueue<>();
                        responseQueues.put(responseMessage.getClientID(), clientQueue);
                    }
                    clientQueue.add(new ConnectionManager.Packet(request.getTag(), responseMessage));
                    logInfo("Response added to client-specific queue for UserID " + responseMessage.getClientID());
                });
            }
        }
    }

    // Check if the current value matches the expected value
    private boolean matchesCondition(String key, byte[] expectedValue) {
        byte[] currentValue = valueConditionMap.get(key);
        return currentValue != null && java.util.Arrays.equals(currentValue, expectedValue);
    }

    private void shutDownHookThread() {
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            logInfo("Shutting down server...");
            stop();
        }));
    }

    public void stop() {
        this.running = false;
        try {
            if (clientConnectionHandler != null) clientConnectionHandler.interrupt();
            if (serverWorker != null) serverWorker.interrupt();
        } catch (Exception e) {
            logError("Error during server stop: " + e.getMessage());
        }
    }


    // Logging utility methods
    private void logInfo(String message) {
        System.out.println("[INFO] " + message);
    }

    private void logError(String message) {
        System.err.println("[ERROR] " + message);
    }

    private void logWarning(String message) {
        System.out.println("[WARNING] " + message);
    }
}