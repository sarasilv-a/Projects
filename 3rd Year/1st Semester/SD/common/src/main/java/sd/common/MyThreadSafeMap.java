package sd.common;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.util.Collection;

public class MyThreadSafeMap<K, V> {
    private final Map<K, V> map;
    private final ReadWriteLock lock;

    public MyThreadSafeMap() {
        this.map = new HashMap<>();
        this.lock = new ReentrantReadWriteLock();
    }

    public V get(K key) {
        this.lock.readLock().lock();
        try {
            return this.map.get(key);
        } finally {
            this.lock.readLock().unlock();
        }
    }

    public void put(K key, V value) {
        this.lock.writeLock().lock();
        try {
            this.map.put(key, value);
        } finally {
            this.lock.writeLock().unlock();
        }
    }

    public boolean containsKey(K key) {
        this.lock.readLock().lock();
        try {
            return this.map.containsKey(key);
        } finally {
            this.lock.readLock().unlock();
        }
    }

    public boolean remove(K key) {
        this.lock.writeLock().lock();
        try {
            return this.map.remove(key) != null;
        } finally {
            this.lock.writeLock().unlock();
        }
    }

    public Set<Map.Entry<K,V>> entrySet() {
        this.lock.readLock().lock();
        try {
            return this.map.entrySet();
        } finally {
            this.lock.readLock().unlock();
        }
    }

    public int size() {
        this.lock.readLock().lock();
        try {
            return this.map.size();
        } finally {
            this.lock.readLock().unlock();
        }
    }

    public boolean isEmpty() {
        this.lock.readLock().lock();
        try {
            return this.map.isEmpty();
        } finally {
            this.lock.readLock().unlock();
        }
    }

    public V computeIfAbsent(K key, java.util.function.Function<? super K, ? extends V> mappingFunction) {
        this.lock.writeLock().lock();
        try {
            return this.map.computeIfAbsent(key, mappingFunction);
        } finally {
            this.lock.writeLock().unlock();
        }
    }

public Collection<V> values() {
        this.lock.readLock().lock();
        try {
            return this.map.values();
        } finally {
            this.lock.readLock().unlock();
        }
    }
}