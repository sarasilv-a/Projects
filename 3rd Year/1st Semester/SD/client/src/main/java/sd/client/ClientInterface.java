package sd.client;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

public class ClientInterface {
    public static void main(String[] args) {
        try (Scanner inputScanner = new Scanner(System.in)) {
            Client client = new Client();
            int authClientID = -1;

            while (authClientID < 0) {
                System.out.println("1 - Login\n2 - Register");
                int input = inputScanner.nextInt();
                if (input == 1) {
                    System.out.println("Write username and password in separate lines");

                    System.out.print("Username: ");
                    String username = inputScanner.next();
                    System.out.print("Password: ");
                    String password = inputScanner.next();

                    authClientID = client.loginUser(username, password);

                    if (authClientID == -1) {
                        System.out.println("Invalid credentials. Please try again.");
                    } else {
                        System.out.println("User: " + username + " with user id of " + authClientID);
                    }
                } else if (input == 2) {
                    System.out.print("Username: ");
                    String username = inputScanner.next();
                    System.out.print("Password: ");
                    String password = inputScanner.next();

                    authClientID = client.registerNewUser(username, password);
                    if (authClientID == -1)
                        System.out.println("Could not register user");
                    else {
                        System.out.println("User: " + username + " registered with user id of " + authClientID);
                    }
                }
            }

            client.startReceivingThread();

            while (true) {
                System.out.println("1 - Put\n2 - Get\n3 - MultiPut\n4 - MultiGet\n5 - GetWhen\n6 - PutCondition\n0 - Exit");
                int input = inputScanner.nextInt();
                if (input == 1) {
                    System.out.print("Key: ");
                    String key = inputScanner.next();
                    System.out.print("Value: ");
                    String value = inputScanner.next();

                    byte[] valueBytes = value.getBytes();
                    client.put(key, valueBytes, authClientID);

                } else if (input == 2) {
                    System.out.print("Write key: ");
                    String key = inputScanner.next();
                    byte[] value = client.get(key, authClientID);
                    System.out.println("Value: " + new String(value));

                } else if (input == 3) {
                    System.out.println("Enter the number of key-value pairs to add: ");
                    int count = inputScanner.nextInt();
                    Map<String, byte[]> pairs = new HashMap<>();
                    for (int i = 0; i < count; i++) {
                        System.out.print("Key: ");
                        String key = inputScanner.next();
                        System.out.print("Value: ");
                        String value = inputScanner.next();
                        pairs.put(key, value.getBytes());
                    }
                    client.multiPut(pairs);

                } else if (input == 4) {
                    System.out.println("Enter the number of keys to retrieve: ");
                    int count = inputScanner.nextInt();
                    Set<String> keys = IntStream.range(0, count)
                            .mapToObj(i -> {
                                System.out.print("Key: ");
                                return inputScanner.next();
                            })
                            .collect(Collectors.toSet());
                    Map<String, byte[]> values = client.multiGet(keys);
                    values.forEach((key, value) -> System.out.println("Key: " + key + ", Value: " + new String(value)));

                } else if (input == 5) {
                    System.out.print("Key to retrieve: ");
                    String key = inputScanner.next();
                    System.out.print("Conditional Key: ");
                    String keyCond = inputScanner.next();
                    System.out.print("Conditional Value: ");
                    String valueCond = inputScanner.next();

                    try {
                        byte[] result = client.getWhen(key, keyCond, valueCond.getBytes(), authClientID);
                        System.out.println("Value for key '" + key + "': " + new String(result));
                    } catch (IOException e) {
                        System.err.println("Error in getWhen request: " + e.getMessage());
                    }

                } else if (input == 6) {
                    System.out.print("Conditional Key: ");
                    String keyCond = inputScanner.next();
                    System.out.print("Conditional Value: ");
                    String valueCond = inputScanner.next();

                    try {
                        client.putCondition(keyCond, valueCond.getBytes());
                        System.out.println("PutCondition completed for key '" + keyCond + "'.");
                    } catch (Exception e) {
                        System.err.println("Error in putCondition request: " + e.getMessage());
                    }

                } else if (input == 0) {
                    client.closeClient();
                    break;
                }
            }
        } catch (Exception e) {
            System.out.println("Error: " + e.getMessage());
        }
    }
}
