package sd.client;

import sd.common.*;

import java.io.IOException;
import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import java.lang.management.MemoryUsage;
import java.util.Scanner;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class ClientMultiThreadTester {

    public static void main(String[] args) {
        try (Scanner scanner = new Scanner(System.in)) {
            // Create the client
            Client client = new Client();

            // Register a new user
            String username = "fer";
            String password = "fer";
            System.out.println("Registering user...");
            int authClientID = client.registerNewUser(username, password);

            if (authClientID < 0) {
                System.out.println("Authentication failed.");
                return;
            }

            System.out.println("User registered successfully with ID: " + authClientID);

            client.startReceivingThread();

            // Get user input for number of threads and total operations
            System.out.print("Enter the number of threads: ");
            int numThreads = scanner.nextInt();
            System.out.print("Enter the total number of operations: ");
            int totalOperations = scanner.nextInt();

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
                        client.put(key, value.getBytes(), authClientID);
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
                        byte[] value = client.get(key, authClientID);
                    } catch (IOException e) {
                        System.err.println("Error in get request for key" + keyIndex + ": " + e.getMessage());
                    }
                });
            }

            executorService.shutdown();
            while (!executorService.isTerminated()) {
                // Wait for all threads to complete
            }

            long endTime = System.currentTimeMillis();
            long totalTime = endTime - startTime;
            double averageTimePerOperation = (double) totalTime / totalOperations;

            MemoryUsage afterMemoryUsage = memoryBean.getHeapMemoryUsage();
            long usedMemoryAfter = afterMemoryUsage.getUsed();
            long memoryUsedByThreads = usedMemoryAfter - usedMemoryBefore;
            double memoryUsedPerThreadMB = ((double) memoryUsedByThreads / numThreads) / (1024 * 1024);

            System.out.println("All threads completed.");
            System.out.println("Total time taken: " + totalTime + " ms");
            System.out.println("Total threads: " + numThreads);
            System.out.println("Total operations: " + totalOperations);
            System.out.println("Average time per operation: " + averageTimePerOperation + " ms");
            System.out.println("Total memory used by threads: " + (memoryUsedByThreads / (1024 * 1024)) + " MB");
            System.out.println("Average memory used per thread: " + memoryUsedPerThreadMB + " MB");

        } catch (IOException e) {
            System.err.println("Error initializing client: " + e.getMessage());
        }
    }
}
