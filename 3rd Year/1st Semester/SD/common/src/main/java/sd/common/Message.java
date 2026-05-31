package sd.common;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;

public abstract class Message {
    private final int clientID;
    private final String subclassName;

    public Message() {
        this.clientID = 0;
        this.subclassName = "";
    }

    public Message(int ClientID, String subclassName) {
        this.clientID = ClientID;
        this.subclassName = subclassName;
    }

    public String getSubclassName() {
        return this.subclassName;
    }

    public int getClientID() {
        return this.clientID;
    }

    public void serialize(DataOutputStream out) throws IOException {
        out.writeInt(clientID);
        out.writeUTF(subclassName);
        this.serializeSubclass(out);
    }

    public static Message deserialize(DataInputStream in) throws IOException, ClassNotFoundException, NoSuchMethodException, InvocationTargetException, InstantiationException, IllegalAccessException {
        int clientID = in.readInt();
        String subName = in.readUTF();
        Class<?> message = Class.forName(subName);
        Message castedMessage = (Message) message.getDeclaredConstructor().newInstance();
        return castedMessage.deserializeSubclass(in, clientID);
    }

    protected abstract void serializeSubclass(DataOutputStream out) throws IOException;
    protected abstract Message deserializeSubclass(DataInputStream in, int clientID) throws IOException;

    public String toString() {
        return "Message{" + "subclassName=" + this.subclassName + '\'' + '}';
    }
}