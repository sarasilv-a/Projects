package sd.common;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;

public class GetWhenRequest extends Message {
    private String key;
    private String keyCond;
    private byte[] valueCond;

    public GetWhenRequest() {
        super(0, GetWhenRequest.class.getName());
        this.key = "";
        this.keyCond = "";
        this.valueCond = new byte[0];
    }

    public GetWhenRequest(int clientID, String key, String keyCond, byte[] valueCond) {
        super(clientID, GetWhenRequest.class.getName());
        this.key = key;
        this.keyCond = keyCond;
        this.valueCond = valueCond;
    }

    public String getKey() {
        return key;
    }

    public String getKeyCond() {
        return keyCond;
    }

    public byte[] getValueCond() {
        return valueCond;
    }

    @Override
    protected void serializeSubclass(DataOutputStream out) throws IOException {
        out.writeUTF(key);
        out.writeUTF(keyCond);
        out.writeInt(valueCond.length);
        out.write(valueCond);
    }

    @Override
    protected Message deserializeSubclass(DataInputStream in, int clientID) throws IOException {
        String key = in.readUTF();
        String keyCond = in.readUTF();
        int length = in.readInt();
        byte[] valueCond = new byte[length];
        in.readFully(valueCond);
        return new GetWhenRequest(clientID, key, keyCond, valueCond);
    }

    @Override
    public String toString() {
        return super.toString() + " GetWhenRequest{" +
                "key='" + key + '\'' +
                ", keyCond='" + keyCond + '\'' +
                ", valueCond=" + new String(valueCond) +
                '}';
    }
}
