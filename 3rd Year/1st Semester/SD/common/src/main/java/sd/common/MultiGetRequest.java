package sd.common;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.util.Set;

public class MultiGetRequest extends Message {
    private Set<String> keys;

    public MultiGetRequest() {
        super(0, MultiGetRequest.class.getName());
        this.keys = Set.of();
    }

    public MultiGetRequest(int clientID, Set<String> keys) {
        super(clientID, MultiGetRequest.class.getName());
        this.keys = keys;
    }

    public Set<String> getKeys() {
        return keys;
    }

    @Override
    protected void serializeSubclass(DataOutputStream out) throws IOException {
        out.writeInt(keys.size());
        for (String key : keys) {
            out.writeUTF(key);
        }
    }

    @Override
    protected Message deserializeSubclass(DataInputStream in, int clientID) throws IOException {
        int size = in.readInt();
        Set<String> keys = new java.util.HashSet<>(Set.of());
        for (int i = 0; i < size; i++) {
            keys.add(in.readUTF());
        }
        return new MultiGetRequest(clientID, keys);
    }

    @Override
    public String toString() {
        return super.toString() + " MultiGetRequest{" + "keys size=" + keys.size() + '}';
    }
}
