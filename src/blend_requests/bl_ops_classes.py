# Copyright 2025 James Crowther
# SPDX-License-Identifier: GPL-3.0-only

import time
from typing import Set
import uuid

import bpy
import zmq
from cr_core.event_bus import BusEvent


# STRING CONSTANTS
CANCELLED = {"CANCELLED"}
FINISHED = {"FINISHED"}
RUNNING_MODAL = {"RUNNING_MODAL"}
PASS_THROUGH = {"PASS_THROUGH"}

zmq_ctx = zmq.Context.instance()


class BR_OT_event_bus_base(bpy.types.Operator):

    subscription_topic: bytes
    time_out: float = 30.0

    def publish_event(self, audience: bytes, topic: bytes, body: bytes):
        bevent = BusEvent(audience, topic, body, self.audience_id.bytes)
        self.pub.send_multipart(bevent.serialise())

    def invoke(self, bl_ctx: bpy.types.Context, event: bpy.types.Event):

        audience_id = uuid.uuid4()
        self.sub = event_bus.get_subscribed_socket(
            [b".".join([audience_id.bytes, self.subscription_topics])]
        )
        self.pub = event_bus.get_pub_to_eventbus_sock()

        wm = bl_ctx.window_manager
        wm.modal_handler.add(self)

        self.timer = wm.event_timer_add(0.064, window=bl_ctx.window)
        self.audience_id = audience_id

        self.request()

        return RUNNING_MODAL

    def request(self):
        pass

    def modal(self, bl_ctx: bpy.types.Context, event: bpy.types.Event) -> Set[str]:

        start_time = time.time()
        if event.type == "TIMER":
            ev = self.sub.poll(0)

            if ev == zmq.POLLIN:
                return self.execute(bl_ctx)

        if timed_out(start_time, self.time_out):
            return CANCELLED

        return PASS_THROUGH

    def execute(self, bl_ctx: bpy.types.Context) -> Set[str]:

        result = self.handle_response()

        if self.timer is not None:
            wm = bl_ctx.window_manager
            wm.event_timer_remove(self.timer)

        self.pub.close()
        self.sub.close()

        return result

    def handle_response(self) -> Set[str]: ...
