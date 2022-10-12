import os
import asyncio
import traceback

from nio import (
    AsyncClient,
    AsyncClientConfig,
    KeyVerificationCancel,
    KeyVerificationEvent,
    KeyVerificationKey,
    KeyVerificationMac,
    KeyVerificationStart,
    LocalProtocolError,
    ToDeviceError,
)

class Callbacks(object):
    def __init__(self, client):
        self.client = client

    async def to_device_callback(self, event):
        try:
            client = self.client

            if isinstance(event, KeyVerificationStart):
                if "emoji" not in event.short_authentication_string:
                    print(
                        "Other device does not support emoji verification "
                        f"{event.short_authentication_string}."
                    )
                    return
                resp = await client.accept_key_verification(event.transaction_id)
                if isinstance(resp, ToDeviceError):
                    print(f"accept_key_verification failed with {resp}")

                sas = client.key_verifications[event.transaction_id]

                todevice_msg = sas.share_key()
                resp = await client.to_device(todevice_msg)
                if isinstance(resp, ToDeviceError):
                    print(f"to_device failed with {resp}")

            elif isinstance(event, KeyVerificationCancel):
                print(
                    f"Verification has been cancelled by {event.sender} "
                    f'for reason "{event.reason}".'
                )

            elif isinstance(event, KeyVerificationKey):
                print(f"Verification request from {event.sender}: ")
                sas = client.key_verifications[event.transaction_id]
                print(f"{sas.get_emoji()}")

                resp = await client.confirm_short_auth_string(event.transaction_id)
                if isinstance(resp, ToDeviceError):
                    print(f"confirm_short_auth_string failed with {resp}")
                
            elif isinstance(event, KeyVerificationMac):
                sas = client.key_verifications[event.transaction_id]
                try:
                    todevice_msg = sas.get_mac()
                except LocalProtocolError as e:
                    # e.g. it might have been cancelled by ourselves
                    print(
                        f"Cancelled or protocol error: Reason: {e}.\n"
                        f"Verification with {event.sender} not concluded. "
                        "Try again?"
                    )
                else:
                    resp = await client.to_device(todevice_msg)
                    if isinstance(resp, ToDeviceError):
                        print(f"to_device failed with {resp}")
                    print(
                        f"sas.we_started_it = {sas.we_started_it}\n"
                        f"sas.sas_accepted = {sas.sas_accepted}\n"
                        f"sas.canceled = {sas.canceled}\n"
                        f"sas.timed_out = {sas.timed_out}\n"
                        f"sas.verified = {sas.verified}\n"
                        f"sas.verified_devices = {sas.verified_devices}\n"
                    )
                    print(
                        "Emoji verification was successful!\n"
                        "Hit Control-C to stop the program or "
                        "initiate another Emoji verification from "
                        "another device or room."
                    )
            else:
                print(
                    f"Received unexpected event type {type(event)}. "
                    f"Event is {event}. Event will be ignored."
                )
        except BaseException:
            print(traceback.format_exc())


async def get_client(homeserver, user_id, password, device_id, store_path) -> AsyncClient:
    if not os.path.exists(store_path):
        os.makedirs(store_path)

    client = AsyncClient(
        homeserver,
        user_id,
        store_path=store_path,
        device_id=device_id,
        config=AsyncClientConfig(
            max_limit_exceeded=0,
            max_timeouts=0,
            store_sync_tokens=True,
            encryption_enabled=True,
        ),
    )
    await client.login(password=password)

    
    callbacks = Callbacks(client)
    client.add_to_device_callback(callbacks.to_device_callback, (KeyVerificationEvent,))
    if client.should_upload_keys:
        await client.keys_upload()

    asyncio.create_task(client.sync_forever(timeout=30000, full_state=True))
    await asyncio.sleep(1)

    return client

