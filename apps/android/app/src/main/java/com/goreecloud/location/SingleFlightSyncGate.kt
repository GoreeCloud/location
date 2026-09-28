package com.goreecloud.location

import java.util.concurrent.atomic.AtomicBoolean

/**
 * Process-wide gate preventing overlapping queue flushes from the foreground collector,
 * JobScheduler retry path, and user-triggered manual sync.
 *
 * The gate contains no sample data and does not transfer queue or credential authority.
 */
object SingleFlightSyncGate {
    private val running = AtomicBoolean(false)

    fun tryEnter(): Boolean = running.compareAndSet(false, true)

    fun leave() {
        running.set(false)
    }

    inline fun <T> runIfAvailable(block: () -> T): T? {
        if (!tryEnter()) return null
        return try {
            block()
        } finally {
            leave()
        }
    }
}
