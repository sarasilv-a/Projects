package sd.client;

import sd.common.*;

import java.io.IOException;
import java.net.Socket;
import java.util.Map;
import java.util.Set;

public class Client {

    private int clientID;
    private final Socket socket;
    private final ConnectionManager serverConnection;

    public Client () throws IOException {
        this.socket = new Socket("localhost", 8080);
        this.serverConnection = new ConnectionManager(this.socket);
    }

    public void startReceivingThread() {
        this.serverConnection.startReceivingThread();
    }

    public void put(String key, byte[] value, int clientID) throws IOException {
        PutRequest putRequest = new PutRequest(clientID, key, value);
        serverConnection.send(Thread.currentThread().threadId(), putRequest);
        PutResponse response = (PutResponse) serverConnection.receive(Thread.currentThread().threadId());
        System.out.println("Put response: " + response);
    }

    public byte[] get(String key, int clientID) throws IOException {
        GetRequest getRequest = new GetRequest(clientID ,key);
        serverConnection.send(Thread.currentThread().threadId(), getRequest);
        GetResponse response = (GetResponse) serverConnection.receive(Thread.currentThread().threadId());
        return response.getValue();
    }

    public void multiPut(Map<String, byte[]> pairs) throws IOException {
        MultiPutRequest multiPutRequest = new MultiPutRequest(clientID, pairs);
        serverConnection.send(Thread.currentThread().threadId(), multiPutRequest);
        MultiPutResponse response = (MultiPutResponse) serverConnection.receive(Thread.currentThread().threadId());
        System.out.println("MultiPut response: " + response);
    }

    public Map<String, byte[]> multiGet(Set<String> keys) throws IOException {
        MultiGetRequest multiGetRequest = new MultiGetRequest(clientID, keys);
        serverConnection.send(Thread.currentThread().threadId(), multiGetRequest);
        MultiGetResponse response = (MultiGetResponse) serverConnection.receive(Thread.currentThread().threadId());
        return response.getPairs();
    }

    public byte[] getWhen(String key, String keyCond, byte[] valueCond, int clientID) throws IOException {
        GetWhenRequest getWhenRequest = new GetWhenRequest(clientID, key, keyCond, valueCond);
        serverConnection.send(Thread.currentThread().threadId(), getWhenRequest);
        GetResponse response = (GetResponse) serverConnection.receive(Thread.currentThread().threadId());
        return response.getValue();
    }

    public void putCondition(String keyCond, byte[] valueCond) throws IOException {
        PutConditionRequest putConditionRequest = new PutConditionRequest(clientID, keyCond, valueCond);
        serverConnection.send(Thread.currentThread().threadId(), putConditionRequest);
        PutResponse response = (PutResponse) serverConnection.receive(Thread.currentThread().threadId());
    }


    public int registerNewUser(String username, String password) throws IOException {
        AuthRequest newUser = new AuthRequest(1, username, password);
        serverConnection.send(Thread.currentThread().threadId(), newUser);
        AuthResponse response = (AuthResponse) serverConnection.simpleReceive(Thread.currentThread().threadId());

        System.out.println(response.toString());

        this.clientID = response.getClientID();

        return response.getClientID();
    }

    public int loginUser(String username, String password) throws IOException {
        AuthRequest user = new AuthRequest(2, username, password);
        serverConnection.send(Thread.currentThread().threadId(), user);
        AuthResponse response = (AuthResponse) serverConnection.simpleReceive(Thread.currentThread().threadId());

        System.out.println(response.toString());

        this.clientID = response.getClientID();

        return response.getClientID();
    }

    public void closeClient() {
        try {
            this.socket.close();
            this.serverConnection.close();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}
