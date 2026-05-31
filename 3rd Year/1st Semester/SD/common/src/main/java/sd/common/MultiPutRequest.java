package sd.common;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
public class MultiPutRequest extends Message {
    private Map<String, byte[]> pairs;

    public MultiPutRequest() {
        super(0, MultiPutRequest.class.getName());
        this.pairs = new HashMap<>();
    }

    public MultiPutRequest(int clientID, Map<String, byte[]> pairs) {
        super(clientID, MultiPutRequest.class.getName());
        this.pairs = pairs;
    }

    public Map<String, byte[]> getPairs() {
        return pairs;
    }

    @Override
    protected void serializeSubclass(DataOutputStream out) throws IOException {
        out.writeInt(pairs.size());
        for (Map.Entry<String, byte[]> entry : pairs.entrySet()) {
            out.writeUTF(entry.getKey());
            byte[] value = entry.getValue();
            out.writeInt(value.length);
            out.write(value);
        }
    }

    @Override
    protected Message deserializeSubclass(DataInputStream in, int clientID) throws IOException {
        int size = in.readInt();
        Map<String, byte[]> pairs = new HashMap<>();
        for (int i = 0; i < size; i++) {
            String key = in.readUTF();
            int length = in.readInt();
            byte[] value = new byte[length];
            in.readFully(value);
            pairs.put(key, value);
        }
        return new MultiPutRequest(clientID, pairs);
    }

    @Override
    public String toString() {
        return super.toString() + " MultiPutRequest{" + "pairs size=" + pairs.size() + '}';
    }
}
