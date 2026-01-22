I'm using mkdocs to write docs for my chat completion endpoint

The endpoint can be interacted via both rest api or client

The client is in sequrity_api/client.py (project sequrity_api): SequrityClient.control.create_chat_completion

The rest api endpoint is defined in secure-orchestrator/endpoint-v1.py (project secure-orchestrator). You may also find /home/cheng/Sequrity/secure-orchestrator/docs/sequrity/endpoint-api.md useful for understanding custom headers.

Use content tab markdown extension for sequrity client and rest api

This is an example of content tab markdown extension:

`````
=== "C"

    ``` c
    #include <stdio.h>

    int main(void) {
      printf("Hello world!\n");
      return 0;
    }
    ```

=== "C++"

    ``` c++
    #include <iostream>

    int main(void) {
      std::cout << "Hello world!" << std::endl;
      return 0;
    }
    ```
`````