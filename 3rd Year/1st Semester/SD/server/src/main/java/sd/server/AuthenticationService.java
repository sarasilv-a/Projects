package sd.server;

import sd.common.AuthRequest;
import sd.common.MyThreadSafeMap;
import sd.common.User;

import java.util.concurrent.atomic.AtomicInteger;

public class AuthenticationService {
    private final MyThreadSafeMap<String, User> users = new MyThreadSafeMap<>();
    private final AtomicInteger authenticatedUsers = new AtomicInteger(0);

    private boolean register(String username, String password) {
        if (users.containsKey(username)) {
            return false;
        }
        users.put(username, new User(username, password));
        return true;
    }

    private boolean login(String username, String password) {
        if (!users.containsKey(username)) {
            return false;
        }
        User user = users.get(username);
        return user.getPassword().equals(password);
    }

    public int authenticateUser(AuthRequest request) {
        if(request.getType() == 1) { // register
            if (register(request.getUsername(), request.getPassword())) {
                System.out.println("[INFO] User registered: " + request.getUsername());
                return authenticatedUsers.incrementAndGet();
            }
        } else if(request.getType() == 2) { // login
            if (login(request.getUsername(), request.getPassword())) {
                System.out.println("[INFO] User authenticated: " + request.getUsername());
                return authenticatedUsers.incrementAndGet();
            }
        }
        return -1;
    }

    public int getAuthenticatedUsers() {
        return authenticatedUsers.get();
    }
}
