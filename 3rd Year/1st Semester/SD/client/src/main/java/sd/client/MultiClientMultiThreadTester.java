package sd.client;

import sd.common.*;

import java.io.IOException;
import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import java.lang.management.MemoryUsage;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class MultiClientMultiThreadTester {

    public static void main(String[] args) {
        try (Scanner scanner = new Scanner(System.in)) {

            System.out.print("Enter the number of clients to connect: ");
            int numClients = scanner.nextInt();

            System.out.print("Enter the number of threads per client: ");
            int numThreads = scanner.nextInt();

            System.out.print("Enter the total number of operations per client: ");
            int totalOperations = scanner.nextInt();

            List<ClientConfig> clientConfigs = new ArrayList<>();
            List<Client> clients = new ArrayList<>();

            // Register and configure clients
            for (int i = 1; i <= numClients; i++) {
                String username = "user" + i;
                String password = "pass" + i;

                System.out.println("Registering client " + i + "...");
                Client client = new Client();
                int authClientID = client.registerNewUser(username, password);

                if (authClientID < 0) {
                    System.out.println("Authentication failed for client " + i + ". Skipping...");
                    continue;
                }

                System.out.println("Client " + i + " registered successfully with ID: " + authClientID);
                client.startReceivingThread();
                clients.add(client);

                // Use the same configuration for all clients
                clientConfigs.add(new ClientConfig(client, authClientID, numThreads, totalOperations, i));
            }

            // Execute all clients simultaneously
            ExecutorService clientExecutor = Executors.newFixedThreadPool(clients.size());

            for (ClientConfig config : clientConfigs) {
                clientExecutor.submit(() -> executeClient(config));
            }

            clientExecutor.shutdown();
            try {
                if (!clientExecutor.awaitTermination(5, TimeUnit.MINUTES)) {
                    System.err.println("Timeout: Not all clients completed their operations.");
                }
            } catch (InterruptedException e) {
                System.err.println("Execution interrupted while waiting for clients to finish.");
            }

            System.out.println("\nAll clients have completed their operations.");

        } catch (IOException e) {
            System.err.println("Error initializing clients: " + e.getMessage());
        }
    }

    private static void executeClient(ClientConfig config) {
        Client client = config.client;
        int clientIndex = config.clientIndex; // Use o índice correto do cliente
        int numThreads = config.numThreads;
        int totalOperations = config.totalOperations;

        int putOperations = totalOperations / 2;
        int getOperations = totalOperations / 2;

        ExecutorService executorService = Executors.newFixedThreadPool(numThreads);

        MemoryMXBean memoryBean = ManagementFactory.getMemoryMXBean();
        MemoryUsage beforeMemoryUsage = memoryBean.getHeapMemoryUsage();
        long usedMemoryBefore = beforeMemoryUsage.getUsed();

        long startTime = System.currentTimeMillis();

        for (int i = 1; i <= putOperations; i++) {
            int keyIndex = i;
            executorService.submit(() -> {
                try {
                    String key = "key" + keyIndex;
                    String value = "value" + keyIndex;
                    client.put(key, value.getBytes(), config.authClientID);
                } catch (IOException e) {
                    System.err.println("Error in put request for key" + keyIndex + ": " + e.getMessage());
                }
            });
        }

        for (int i = 1; i <= getOperations; i++) {
            int keyIndex = i;
            executorService.submit(() -> {
                try {
                    String key = "key" + keyIndex;
                    byte[] value = client.get(key, config.authClientID);
                } catch (IOException e) {
                    System.err.println("Error in get request for key" + keyIndex + ": " + e.getMessage());
                }
            });
        }

        executorService.shutdown();
        try {
            if (!executorService.awaitTermination(5, TimeUnit.MINUTES)) {
                System.err.println("Timeout: Client " + clientIndex + " did not complete its tasks.");
            }
        } catch (InterruptedException e) {
            System.err.println("Execution interrupted for Client " + clientIndex + ".");
        }

        long endTime = System.currentTimeMillis();
        long totalTime = endTime - startTime;
        double averageTimePerOperation = (double) totalTime / totalOperations;

        MemoryUsage afterMemoryUsage = memoryBean.getHeapMemoryUsage();
        long usedMemoryAfter = afterMemoryUsage.getUsed();
        long memoryUsedByThreads = usedMemoryAfter - usedMemoryBefore;
        double memoryUsedPerThreadMB = ((double) memoryUsedByThreads / numThreads) / (1024 * 1024);

        System.out.println("\nResults for Client " + clientIndex + ":");
        System.out.println("Total time taken: " + totalTime + " ms");
        System.out.println("Total threads: " + numThreads);
        System.out.println("Total operations: " + totalOperations);
        System.out.println("Average time per operation: " + averageTimePerOperation + " ms");
        System.out.println("Total memory used by threads: " + (memoryUsedByThreads / (1024 * 1024)) + " MB");
        System.out.println("Average memory used per thread: " + memoryUsedPerThreadMB + " MB");
    }

    // Helper class to store client configuration
    private static class ClientConfig {
        Client client;
        int authClientID;
        int numThreads;
        int totalOperations;
        int clientIndex;

        ClientConfig(Client client, int authClientID, int numThreads, int totalOperations, int clientIndex) {
            this.client = client;
            this.authClientID = authClientID;
            this.numThreads = numThreads;
            this.totalOperations = totalOperations;
            this.clientIndex = clientIndex;
        }
    }
}
