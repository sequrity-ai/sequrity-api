# Using Header Classes

Sequrity provides typed [Pydantic](https://docs.pydantic.dev/) classes for each custom header
(`X-Features`, `X-Policy`, `X-Config`).
These classes ensure you construct valid header values with the correct structure and field types.

??? tip "Download Tutorial Scripts"

    - [Sequrity Client version](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/getting_started/custom_headers/sequrity_client.py)
    - [REST API version](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/getting_started/custom_headers/rest_api.py)

## Sequrity Client

### Imports

```python
--8<-- "examples/control/getting_started/custom_headers/sequrity_client.py:imports"
```

### Building Headers

```python
--8<-- "examples/control/getting_started/custom_headers/sequrity_client.py:build_headers"
```

### Sending the Request

Pass the header objects directly to [`chat.create`][sequrity.control.resources.chat.ChatResource.create]:

```python
--8<-- "examples/control/getting_started/custom_headers/sequrity_client.py:send_request"
```

## REST API

For raw HTTP calls, use `dump_for_headers()` to serialize each object to a JSON string
ready to be placed in the header value.

### Imports

There are three main header classes available from `sequrity.control.types` corresponding to the three custom headers:

- [`FeaturesHeader`][sequrity.control.types.headers.FeaturesHeader]
- [`SecurityPolicyHeader`][sequrity.control.types.headers.SecurityPolicyHeader] — with [`PolicyCode`][sequrity.control.types.headers.PolicyCode] from `sequrity.control.types.headers`
- [`FineGrainedConfigHeader`][sequrity.control.types.headers.FineGrainedConfigHeader] — with [`FsmOverrides`][sequrity.control.types.headers.FsmOverrides] and [`ResponseFormatOverrides`][sequrity.control.types.headers.ResponseFormatOverrides] from `sequrity.control.types.headers`

```python
--8<-- "examples/control/getting_started/custom_headers/rest_api.py:imports"
```

### Building and Serializing Headers

Build the header objects as you would with the Sequrity Client, then call `dump_for_headers()` to get the JSON strings for the HTTP headers.

```python
--8<-- "examples/control/getting_started/custom_headers/rest_api.py:build_headers"
```

### Sending the Request

```python
--8<-- "examples/control/getting_started/custom_headers/rest_api.py:chat_completion_func"
```
