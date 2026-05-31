package sd.common;

import java.io.*;
import java.lang.reflect.InvocationTargetException;
import java.net.Socket;
import java.util.*;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.ReentrantLock;

public class ConnectionManager implements AutoCloseable {

    public static class Packet {
        private final long tag;
        private final Message message;

        public Packet(long tag, Message message) {
            this.tag = tag;
            this.message = message;
        }

        public long getTag() {
            return tag;
        }

        public Message getMessage() {
            return message;
        }
    }

    private Socket socket;
    private DataInputStream input;
    private DataOutputStream output;
    private ReentrantLock readLock;
    private ReentrantLock writeLock;
    private ReentrantLock lock;
    private MyThreadSafeMap<Long, Condition> conditions;
    private MyThreadSafeMap<Long, Deque<Message>> messageQueues;
    private Exception connectionException;

    public ConnectionManager(Socket socket) throws IOException {
        this.socket = socket;
        this.input = new DataInputStream(new BufferedInputStream(socket.getInputStream()));
        this.output = new DataOutputStream(new BufferedOutputStream(socket.getOutputStream()));
        this.readLock = new ReentrantLock();
        this.writeLock = new ReentrantLock();
        this.lock = new ReentrantLock();
        this.connectionException = null;
    }

    // This method is used to start a thread that will be responsible for receiving messages
    public void startReceivingThread() {
        this.conditions = new MyThreadSafeMap<>();
        this.messageQueues = new MyThreadSafeMap<>();
        new Thread(() -> {
            try {
                while (true) {
                    Packet receivedPacket = receivePacket();
                    long tag = receivedPacket.getTag();

                    lock.lock();
                    try {
                        if (!messageQueues.containsKey(tag)) {
                            messageQueues.put(tag, new ArrayDeque<>());
                            conditions.put(tag, lock.newCondition());
                        }
                        // Add the received message to the queue and signal the condition
                        messageQueues.get(tag).add(receivedPacket.getMessage());
                        conditions.get(tag).signal();
                    } finally {
                        lock.unlock();
                    }
                }
            } catch (IOException | IllegalAccessException | InvocationTargetException |
                     NoSuchMethodException | InstantiationException | ClassNotFoundException e) {
                handleException(e);
            }
        }).start();
    }

    public void send(long tag, Message message) throws IOException {
        writeLock.lock();
        try {
            output.writeLong(tag);
            message.serialize(output);
            output.flush();
        } finally {
            writeLock.unlock();
        }
    }

    public Message receive(long tag) {
        lock.lock();
        try {
            // If the tag is not in the map, add it
            if (!conditions.containsKey(tag)) {
                conditions.put(tag, lock.newCondition());
                messageQueues.put(tag, new ArrayDeque<>());
            }

            // Wait until a message is received
            Condition condition = conditions.get(tag);
            Deque<Message> queue = messageQueues.get(tag);

            while (queue.isEmpty() && connectionException == null) {
                condition.await();
            }

            if (!queue.isEmpty()) {
                return queue.poll();
            } else {
                throw new RuntimeException(connectionException);
            }
        } catch (InterruptedException e) {
            throw new RuntimeException("Thread interrupted while waiting to receive message", e);
        } finally {
            lock.unlock();
        }
    }

    public Message simpleReceive(long tag) {
        readLock.lock();
        try {
            long receivedTag = input.readLong();
            if (receivedTag != tag) {
                throw new RuntimeException("Received unexpected tag: " + receivedTag);
            }
            return Message.deserialize(input);
        } catch (IOException | ClassNotFoundException | NoSuchMethodException | InstantiationException | IllegalAccessException | InvocationTargetException e) {
            throw new RuntimeException("Error receiving message", e);
        } finally {
            readLock.unlock();
        }
    }

    public Packet receivePacket() throws IOException, ClassNotFoundException, InvocationTargetException, NoSuchMethodException, InstantiationException, IllegalAccessException {
        readLock.lock();
        try {
            long tag = input.readLong();
            Message message = Message.deserialize(input);
            return new Packet(tag, message);
        } finally {
            readLock.unlock();
        }
    }

    private void handleException(Exception e) {
        lock.lock();
        try {
            connectionException = e;
            conditions.values().forEach(Condition::signalAll);
        } finally {
            lock.unlock();
        }
    }

    @Override
    public void close() throws IOException {
        input.close();
        output.close();
        socket.close();
    }
}

