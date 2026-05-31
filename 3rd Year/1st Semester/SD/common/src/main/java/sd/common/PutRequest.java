package sd.common;

import java.io.DataOutputStream;
import java.io.DataInputStream;
import java.io.IOException;

public class PutRequest extends Message {
    private String key;
    private byte[] value;

    public PutRequest() {
        super(0, PutRequest.class.getName());
        this.key = "";
        this.value = new byte[0];
    }

    public PutRequest(int clientID, String key, byte[] value) {
        super(clientID, PutRequest.class.getName());
        this.key = key;
        this.value = value;
    }

    public String getKey() {
        return key;
    }

    public byte[] getValue() {
        return value;
    }

    @Override
    protected void serializeSubclass(DataOutputStream out) throws IOException {
        out.writeUTF(key);
        out.writeInt(value.length);
        out.write(value);
    }

    @Override
    protected Message deserializeSubclass(DataInputStream in, int clientID) throws IOException {
        String key = in.readUTF();
        int length = in.readInt();
        byte[] value = new byte[length];
        in.readFully(value);
        return new PutRequest(clientID, key, value);
    }

    @Override
    public String toString() {
        return super.toString() + " PutRequest{" + "key='" + key + '\'' + ", value length=" + value.length + '}';
    }
}
