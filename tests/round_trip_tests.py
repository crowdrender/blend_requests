# Copyright 2025 James Crowther
# SPDX-License-Identifier: GPL-3.0-only

from typing import Set

import bpy
from crowdrender.cr_core import HOST_APP
from crowdrender.cr_core.event_bus import BusEvent

from blend_requests.bl_ops_classes import FINISHED, BR_OT_event_bus_base


TEST_TOPIC = b"test.topic"


class CR_OT_event_bus_test_2(BR_OT_event_bus_base):

    bl_idname = "crowdrender.event_bus_test_2"
    bl_label = "test op 2"
    subscription_topic = TEST_TOPIC

    @classmethod
    def poll(cls, bl_ctx: bpy.types.Context):
        return True

    def request(self):

        # generate the request event.
        self.publish_event(HOST_APP, self.subscription_topic, b"Hi!")

    def handle_response(self) -> Set[str]:

        bevent = BusEvent.deserialise(self.sub.recv_multipart())
        self.report({"INFO"}, f"got {bevent.body} back from test service.")

        return FINISHED
