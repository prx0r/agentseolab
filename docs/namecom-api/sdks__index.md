> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# SDK Quickstart

> Install and authenticate with the official name.com Core API client libraries for TypeScript, Go, and PHP. Python coming soon.

Official client SDKs for the name.com Core API. They give you typed clients that map directly to the [API reference](/api/v1/reference), so you can start building in minutes.

Use an SDK when you want the fastest path in your language. Prefer raw HTTP when you want full control — both talk to the same API.

## Available packages

| Language             | Install                                    | Status      | Source                                                                                                               |
| -------------------- | ------------------------------------------ | ----------- | -------------------------------------------------------------------------------------------------------------------- |
| TypeScript / Node.js | `npm install @namecom/core-api`            | Available   | [GitHub](https://github.com/namedotcom/core-api-typescript) · [npm](https://www.npmjs.com/package/@namecom/core-api) |
| Go                   | `go get github.com/namedotcom/core-api-go` | Available   | [GitHub](https://github.com/namedotcom/core-api-go)                                                                  |
| PHP                  | `composer require namecom/core-api`        | Available   | [GitHub](https://github.com/namedotcom/core-api-php) · [Packagist](https://packagist.org/packages/namecom/core-api)  |
| Python               | `pip install namecom-core-api`             | Coming soon | GitHub                                                                                                               |

<Note>
  Python (`namecom-core-api`) is not released yet. Rest assured, it's coming soon! In the meantime, you can use standard Python libraries like urllib or requests to access the Core API over HTTPS. We will update this page when the package is available.
</Note>

## Environments and auth

SDKs use the same credentials as curl: **HTTP Basic Auth** with your API username and token. See [Authentication](/guides/authentication) and [Getting Started](/guides/getting-started).

| Environment | Base URL                   | Username                             |
| ----------- | -------------------------- | ------------------------------------ |
| Sandbox     | `https://api.dev.name.com` | `your-username-test` + sandbox token |
| Production  | `https://api.name.com`     | `your-username` + production token   |

Pass the matching base URL (or environment) when you construct the client. Do not mix sandbox credentials with the production host.

## First call

Call `GET /core/v1/hello` to verify install and auth. Examples below use the **sandbox**.

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { NamecomClient } from "@namecom/core-api";

  const client = new NamecomClient({
    username: "your-username-test",
    password: "your-sandbox-token",
    baseUrl: "https://api.dev.name.com",
  });

  const hello = await client.hello();
  console.log(hello.motd);
  ```

  ```go Go theme={null}
  package main

  import (
  	"context"
  	"fmt"
  	"log"

  	"github.com/namedotcom/core-api-go/client"
  	"github.com/namedotcom/core-api-go/option"
  )

  func main() {
  	c := client.NewNamecom(
  		option.WithBaseURL("https://api.dev.name.com"),
  		option.WithBasicAuth("your-username-test", "your-sandbox-token"),
  	)

  	hello, err := c.Hello(context.Background())
  	if err != nil {
  		log.Fatal(err)
  	}
  	fmt.Println(hello.Motd)
  }
  ```

  ```php PHP theme={null}
  <?php

  require __DIR__ . '/vendor/autoload.php';

  use Namecom\NamecomClient;

  $client = new NamecomClient(
      'your-username-test',
      'your-sandbox-token',
      ['baseUrl' => 'https://api.dev.name.com']
  );

  $hello = $client->hello();
  print_r($hello);
  ```

  ```python Python theme={null}
  # Coming soon
  #
  # from namecom_core_api import Namecom
  #
  # client = Namecom(
  #     username="your-username-test",
  #     password="your-sandbox-token",
  #     base_url="https://api.dev.name.com",
  # )
  # print(client.hello().motd)
  ```
</CodeGroup>

<Tip>
  Each GitHub repository includes a README with additional language-specific detail. Prefer that README for advanced configuration; use this page for install, auth, and your first request.
</Tip>

## Next steps

<CardGroup cols={2}>
  <Card title="Reseller Quickstart" icon="shopping-cart" href="/guides/quickstart">
    Search → register → manage with the Core API
  </Card>

  <Card title="API reference" icon="code" href="/api/v1/reference">
    Full endpoint documentation (same surface as the SDKs)
  </Card>

  <Card title="Testing environment" icon="flask" href="/guides/testing-environment">
    Sandbox credentials, credit, and limits
  </Card>

  <Card title="name.com MCP" icon="robot" href="/integrations/mcp/namecom-mcp">
    Call the Core API from AI agents
  </Card>
</CardGroup>
