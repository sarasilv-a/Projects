package sd.common;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;

public class PutConditionRequest extends Message {
    private String key;
    private byte[] value;

    public PutConditionRequest() {
        super(0, PutConditionRequest.class.getName());
        this.key = "";
        this.value = new byte[0];
    }

    public PutConditionRequest(int clientID, String key, byte[] value) {
        super(clientID, PutConditionRequest.class.getName());
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
        return new PutConditionRequest(clientID, key, value);
    }

    @Override
    public String toString() {
        return super.toString() + " PutConditionRequest{" +
                "key='" + key + '\'' +
                ", value length=" + value.length +
                '}';
    }
}
