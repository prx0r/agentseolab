> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Authentication

> How to authenticate with the name.com Core API using HTTP Basic Auth.

The Core API uses **HTTP Basic Authentication** with your name.com API credentials. You can either use cURL's convenient `-u` shorthand or provide the explicit `Authorization` header.

<Info>
  Using `-u username:token` is equivalent to sending `Authorization: Basic <base64(username:token)>`.
</Info>

## Quick Example

```bash theme={null}
curl -u your-username:your-api-token https://api.dev.name.com/core/v1/hello
```

## Understanding Basic Authentication Examples

You may notice some examples show the explicit `Authorization: Basic <encoded-value>` header. This is functionally identical to the simpler cURL shorthand:

```bash theme={null}
# Preferred, user-friendly syntax
curl -u <username>:<API-token> ...
```

The server requires the header format; the `-u` flag tells `curl` to automatically create and Base64-encode your `<username>:<API-token>` string.

If you need to manually generate the required Base64 `<encoded-value>` for use in another tool (or to copy into examples):

1. Combine your credentials: `<username>:<API-token>` (e.g., `janedoe:tok_12345`)
2. Encode the string using one of the following methods:

| Environment              | Command to Generate Encoded Value                                                |          |
| :----------------------- | :------------------------------------------------------------------------------- | -------- |
| **Linux/macOS (Bash)**   | \`echo -n 'janedoe:tok\_12345'                                                   | base64\` |
| **Windows (PowerShell)** | `[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("janedoe:tok_12345"))` |          |

Once you have the encoded value, you can use it with an explicit header:

```bash theme={null}
curl --request GET \
  --url https://api.dev.name.com/core/v1/hello \
  --header 'Authorization: Basic <your-encoded-value>'
```

## Sandbox vs Production

Use your sandbox credentials for the development environment (`https://api.dev.name.com`) and production credentials for `https://api.name.com`.

<CodeGroup>
  ```bash Sandbox theme={null}
  curl -u your-username-test:your-sandbox-token https://api.dev.name.com/core/v1/hello
  ```

  ```bash Production theme={null}
  curl -u your-username:your-api-token https://api.name.com/core/v1/hello
  ```
</CodeGroup>

<Warning>
  If your account has 2FA enabled, enable API Access in Account Settings → Security. Always keep tokens secure and never commit them to source control.
</Warning>
