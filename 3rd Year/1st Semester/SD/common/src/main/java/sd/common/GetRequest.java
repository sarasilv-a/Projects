package sd.common;


import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;

public class GetRequest extends Message {
    private String key;

    public GetRequest() {
        super(0, GetRequest.class.getName());
        this.key = "";
    }

    public GetRequest(int clientID, String key) {
        super(clientID, GetRequest.class.getName());
        this.key = key;
    }

    public String getKey() {
        return key;
    }

    @Override
    protected void serializeSubclass(DataOutputStream out) throws IOException {
        out.writeUTF(key);
    }

    @Override
    protected Message deserializeSubclass(DataInputStream in, int clientID) throws IOException {
        String key = in.readUTF();
        return new GetRequest(clientID, key);
    }

    @Override
    public String toString() {
        return super.toString() + " GetRequest{" + "key='" + key + '\'' + '}';
    }
}
