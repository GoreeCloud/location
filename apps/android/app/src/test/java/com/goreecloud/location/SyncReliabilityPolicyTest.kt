package com.goreecloud.location

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class SyncReliabilityPolicyTest {
    @Test
    fun serverStatesMapToFailClosedOutcomes() {
        assertEquals(SyncOutcome.SUCCESS, SyncRetryPolicy.classifyState("ok"))
        assertEquals(SyncOutcome.OFFLINE, SyncRetryPolicy.classifyState("offline"))
        assertEquals(SyncOutcome.TRACKING_PAUSED, SyncRetryPolicy.classifyState("tracking_paused"))
        assertEquals(
            SyncOutcome.AUTHENTICATION_REVOKED,
            SyncRetryPolicy.classifyState("device_auth_required"),
        )
        assertEquals(
            SyncOutcome.AUTHENTICATION_REVOKED,
            SyncRetryPolicy.classifyState("not_enrolled"),
        )
        assertEquals(
            SyncOutcome.TRANSIENT_SERVER_FAILURE,
            SyncRetryPolicy.classifyState("server_503"),
        )
        assertEquals(
            SyncOutcome.MALFORMED_LOCAL_RECORD,
            SyncRetryPolicy.classifyState("sample_conflict"),
        )
    }

    @Test
    fun retryBackoffIsBoundedAndPauseDoesNotRetry() {
        assertEquals(30_000L, SyncRetryPolicy.decide(SyncOutcome.PENDING_QUEUE, 0).delayMs)
        assertEquals(60_000L, SyncRetryPolicy.decide(SyncOutcome.OFFLINE, 1).delayMs)
        assertEquals(
            30 * 60_000L,
            SyncRetryPolicy.decide(SyncOutcome.TRANSIENT_SERVER_FAILURE, 99).delayMs,
        )

        val paused = SyncRetryPolicy.decide(SyncOutcome.TRACKING_PAUSED, 0)
        assertFalse(paused.shouldRetry)
        assertNull(paused.delayMs)
        assertEquals("tracking-paused", paused.reason)
    }

    @Test
    fun singleFlightGateRejectsOverlapAndReleasesCleanly() {
        assertTrue(SingleFlightSyncGate.tryEnter())
        try {
            assertFalse(SingleFlightSyncGate.tryEnter())
        } finally {
            SingleFlightSyncGate.leave()
        }

        assertTrue(SingleFlightSyncGate.tryEnter())
        SingleFlightSyncGate.leave()
    }
}
