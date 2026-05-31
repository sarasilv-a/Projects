package sd.common;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.util.Arrays;

public class GetResponse extends Message {
    private byte[] value;

    public GetResponse() {
        super(0, GetResponse.class.getName());
        this.value = new byte[0];
    }

    public GetResponse(int clientID, byte[] value) {
        super(clientID, GetResponse.class.getName());
        this.value = value;
    }

    public byte[] getValue() {
        return value;
    }

    @Override
    protected void serializeSubclass(DataOutputStream out) throws IOException {
        out.writeInt(value.length);
        out.write(value);
    }

    @Override
    protected Message deserializeSubclass(DataInputStream in, int clientID) throws IOException {
        int length = in.readInt();
        byte[] value = new byte[length];
        in.readFully(value);
        return new GetResponse(clientID, value);
    }

    @Override
    public String toString() {
        return super.toString() + " GetResponse{" + "value= " + Arrays.toString(value) + ", value length= " + value.length + '}';
    }
}
