> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# HMAC Signature Verification

> Practical examples to verify name.com webhook HMAC signatures including header format, generation steps, and security best practices in common programming languages.

## Signature Format

name.com webhooks include an `X-NAMECOM-SIGNATURE` header containing the HMAC signature with additional security measures. The header value format is:

```
X-NAMECOM-SIGNATURE: algorithmName=encodedSignature,timestamp,nonce
```

Where:

* `algorithmName=encodedSignature` is the HMAC signature (e.g., "sha256=a1b2c3d4...")
* `timestamp` is the Unix timestamp when the signature was generated
* `nonce` is a unique identifier (UUID) to prevent replay attacks

## Signature Generation Process

name.com generates signatures using the following process:

1. Convert payload to object and sort keys alphabetically recursively
2. JSON encode the sorted payload
3. Combine the exact full webhook subscription URL and JSON payload with a pipe delimiter (`<full_webhook_url>|<sorted_json_payload>`)
4. Compute HMAC using the specified algorithm, combined data, and your API token (earliest if multiple exist)
5. Convert binary signature to hexadecimal and prefix with algorithm name
6. Generate Unix timestamp and unique nonce (UUID)
7. Combine signature, timestamp, and nonce as comma-separated values

## Accounts with multiple API tokens

* Webhook HMAC is computed with your account's earliest API v4 token.
* If the account has only one token, that token is the signing key.

## URL Canonicalization Requirement

When verifying `X-NAMECOM-SIGNATURE`, construct the HMAC input using the exact full webhook subscription URL (including scheme, host, and path; include query string if present), not a path-only value.

Canonical input format: `<full_webhook_url>|<sorted_json_payload>`.

## Verification Examples

### PHP

```php theme={null}
<?php

function verifyHmacSignature($payload, $headerValue, $apiToken, $webhookUrl, $maxAgeSeconds = 300) {
    // Parse the header value: signature,timestamp,nonce
    $parts = explode(',', $headerValue);
    if (count($parts) !== 3) {
        throw new InvalidArgumentException('Invalid header format');
    }
    
    list($signaturePart, $timestamp, $nonce) = $parts;
    
    // Validate timestamp to prevent replay attacks
    $currentTime = time();
    if (abs($currentTime - (int)$timestamp) > $maxAgeSeconds) {
        throw new InvalidArgumentException('Signature timestamp is too old');
    }
    
    // Parse the signature to extract algorithm and value
    if (strpos($signaturePart, '=') === false) {
        throw new InvalidArgumentException('Invalid signature format');
    }
    
    list($algorithm, $signatureValue) = explode('=', $signaturePart, 2);
    
    // Convert payload to array and sort keys
    if (!is_array($payload)) {
        $payload = (array)$payload;
    }
    ksort($payload);
    
    // JSON encode the sorted payload
    $jsonPayload = json_encode($payload, JSON_UNESCAPED_SLASHES);
    
    // Combine URL and payload as done in signature generation
    $signatureData = $webhookUrl . '|' . $jsonPayload;
    
    // Compute expected signature
    $expectedSignature = hash_hmac($algorithm, $signatureData, $apiToken, true);
    $expectedHex = bin2hex($expectedSignature);
    
    // Compare signatures using timing-safe comparison
    return hash_equals($expectedHex, $signatureValue);
}

// Example usage
$payload = ['domain' => 'example.com', 'action' => 'created'];
$headerValue = 'sha256=a1b2c3d4e5f6...,1640995200,550e8400-e29b-41d4-a716-446655440000'; // From X-NAMECOM-SIGNATURE header
$apiToken = 'your-api-token';
$webhookUrl = 'https://partner.example.com/webhook/domain-created'; // The exact full webhook subscription URL

try {
    if (verifyHmacSignature($payload, $headerValue, $apiToken, $webhookUrl)) {
        echo "Signature is valid\n";
    } else {
        echo "Signature is invalid\n";
    }
} catch (InvalidArgumentException $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
```

### Python

```python theme={null}
import hmac
import hashlib
import json
import time

def verify_hmac_signature(payload, header_value, api_token, webhook_url, max_age_seconds=300):
    """
    Verify HMAC signature for name.com webhook
    """
    # Parse the header value: signature,timestamp,nonce
    parts = header_value.split(',')
    if len(parts) != 3:
        raise ValueError('Invalid header format')
    
    signature_part, timestamp, nonce = parts
    
    # Validate timestamp to prevent replay attacks
    current_time = int(time.time())
    if abs(current_time - int(timestamp)) > max_age_seconds:
        raise ValueError('Signature timestamp is too old')
    
    # Parse the signature to extract algorithm and value
    if '=' not in signature_part:
        raise ValueError('Invalid signature format')
    
    algorithm, signature_value = signature_part.split('=', 1)
    
    # Convert payload to dict and sort keys
    if not isinstance(payload, dict):
        payload = dict(payload)
    
    # Sort keys alphabetically
    sorted_payload = dict(sorted(payload.items()))
    
    # JSON encode the sorted payload
    json_payload = json.dumps(sorted_payload, separators=(',', ':'), ensure_ascii=False)
    
    # Combine URL and payload as done in signature generation
    signature_data = webhook_url + '|' + json_payload
    
    # Get the hash function based on algorithm
    hash_func = getattr(hashlib, algorithm, None)
    if hash_func is None:
        raise ValueError(f'Unsupported algorithm: {algorithm}')
    
    # Compute expected signature
    expected_signature = hmac.new(
        api_token.encode('utf-8'),
        signature_data.encode('utf-8'),
        hash_func
    ).hexdigest()
    
    # Compare signatures using timing-safe comparison
    return hmac.compare_digest(expected_signature, signature_value)

# Example usage
payload = {'domain': 'example.com', 'action': 'created'}
header_value = 'sha256=a1b2c3d4e5f6...,1640995200,550e8400-e29b-41d4-a716-446655440000'  # From X-NAMECOM-SIGNATURE header
api_token = 'your-api-token'
webhook_url = 'https://partner.example.com/webhook/domain-created'  # The exact full webhook subscription URL

try:
    if verify_hmac_signature(payload, header_value, api_token, webhook_url):
        print("Signature is valid")
    else:
        print("Signature is invalid")
except ValueError as e:
    print(f"Error: {e}")
```

### Go

```go theme={null}
package main

import (
    "crypto/hmac"
    "crypto/sha256"
    "encoding/hex"
    "encoding/json"
    "fmt"
    "sort"
    "strconv"
    "strings"
    "time"
)

func verifyHmacSignature(payload map[string]interface{}, headerValue, apiToken, webhookUrl string, maxAgeSeconds int) (bool, error) {
    // Parse the header value: signature,timestamp,nonce
    parts := strings.Split(headerValue, ",")
    if len(parts) != 3 {
        return false, fmt.Errorf("invalid header format")
    }
    
    signaturePart, timestampStr, nonce := parts[0], parts[1], parts[2]
    
    // Validate timestamp to prevent replay attacks
    timestamp, err := strconv.ParseInt(timestampStr, 10, 64)
    if err != nil {
        return false, fmt.Errorf("invalid timestamp: %v", err)
    }
    
    currentTime := time.Now().Unix()
    if abs(currentTime-timestamp) > int64(maxAgeSeconds) {
        return false, fmt.Errorf("signature timestamp is too old")
    }
    
    // Parse the signature to extract algorithm and value
    signatureParts := strings.SplitN(signaturePart, "=", 2)
    if len(signatureParts) != 2 {
        return false, fmt.Errorf("invalid signature format")
    }
    
    algorithm, signatureValue := signatureParts[0], signatureParts[1]
    
    // Sort keys alphabetically
    keys := make([]string, 0, len(payload))
    for k := range payload {
        keys = append(keys, k)
    }
    sort.Strings(keys)
    
    // Create sorted map
    sortedPayload := make(map[string]interface{})
    for _, k := range keys {
        sortedPayload[k] = payload[k]
    }
    
    // JSON encode the sorted payload
    jsonPayload, err := json.Marshal(sortedPayload)
    if err != nil {
        return false, err
    }
    
    // Combine URL and payload as done in signature generation
    signatureData := webhookUrl + "|" + string(jsonPayload)
    
    // Get the hash function based on algorithm
    var hashFunc func() hash.Hash
    switch algorithm {
    case "sha256":
        hashFunc = sha256.New
    default:
        return false, fmt.Errorf("unsupported algorithm: %s", algorithm)
    }
    
    // Compute expected signature
    mac := hmac.New(hashFunc, []byte(apiToken))
    mac.Write([]byte(signatureData))
    expectedSignature := hex.EncodeToString(mac.Sum(nil))
    
    // Compare signatures using timing-safe comparison
    return hmac.Equal([]byte(expectedSignature), []byte(signatureValue)), nil
}

func abs(x int64) int64 {
    if x < 0 {
        return -x
    }
    return x
}

// Example usage
func main() {
    payload := map[string]interface{}{
        "domain": "example.com",
        "action": "created",
    }
    headerValue := "sha256=a1b2c3d4e5f6...,1640995200,550e8400-e29b-41d4-a716-446655440000" // From X-NAMECOM-SIGNATURE header
    apiToken := "your-api-token"
    webhookUrl := "https://partner.example.com/webhook/domain-created" // The exact full webhook subscription URL
    maxAgeSeconds := 300
    
    valid, err := verifyHmacSignature(payload, headerValue, apiToken, webhookUrl, maxAgeSeconds)
    if err != nil {
        fmt.Printf("Error: %v\n", err)
        return
    }
    
    if valid {
        fmt.Println("Signature is valid")
    } else {
        fmt.Println("Signature is invalid")
    }
}
```

### JavaScript (Node.js)

```javascript theme={null}
const crypto = require('crypto');

function verifyHmacSignature(payload, headerValue, apiToken, webhookUrl, maxAgeSeconds = 300) {
    // Parse the header value: signature,timestamp,nonce
    const parts = headerValue.split(',');
    if (parts.length !== 3) {
        throw new Error('Invalid header format');
    }
    
    const [signaturePart, timestampStr, nonce] = parts;
    
    // Validate timestamp to prevent replay attacks
    const timestamp = parseInt(timestampStr, 10);
    const currentTime = Math.floor(Date.now() / 1000);
    if (Math.abs(currentTime - timestamp) > maxAgeSeconds) {
        throw new Error('Signature timestamp is too old');
    }
    
    // Parse the signature to extract algorithm and value
    if (!signaturePart.includes('=')) {
        throw new Error('Invalid signature format');
    }
    
    const [algorithm, signatureValue] = signaturePart.split('=', 2);
    
    // Convert payload to object and sort keys
    let sortedPayload;
    if (Array.isArray(payload)) {
        sortedPayload = payload;
    } else if (typeof payload === 'object' && payload !== null) {
        // Sort keys alphabetically
        const sortedKeys = Object.keys(payload).sort();
        sortedPayload = {};
        for (const key of sortedKeys) {
            sortedPayload[key] = payload[key];
        }
    } else {
        sortedPayload = payload;
    }
    
    // JSON encode the sorted payload
    const jsonPayload = JSON.stringify(sortedPayload);
    
    // Combine URL and payload as done in signature generation
    const signatureData = webhookUrl + '|' + jsonPayload;
    
    // Compute expected signature
    const expectedSignature = crypto
        .createHmac(algorithm, apiToken)
        .update(signatureData, 'utf8')
        .digest('hex');
    
    // Compare signatures using timing-safe comparison
    return crypto.timingSafeEqual(
        Buffer.from(expectedSignature, 'hex'),
        Buffer.from(signatureValue, 'hex')
    );
}

// Example usage
const payload = { domain: 'example.com', action: 'created' };
const headerValue = 'sha256=a1b2c3d4e5f6...,1640995200,550e8400-e29b-41d4-a716-446655440000'; // From X-NAMECOM-SIGNATURE header
const apiToken = 'your-api-token';
const webhookUrl = 'https://partner.example.com/webhook/domain-created'; // The exact full webhook subscription URL

try {
    if (verifyHmacSignature(payload, headerValue, apiToken, webhookUrl)) {
        console.log('Signature is valid');
    } else {
        console.log('Signature is invalid');
    }
} catch (error) {
    console.error('Error:', error.message);
}
```

### Java

```java theme={null}
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.util.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;

public class HmacVerifier {
    
    public static boolean verifyHmacSignature(Object payload, String headerValue, String apiToken, String webhookUrl, int maxAgeSeconds) 
            throws Exception {
        
        // Parse the header value: signature,timestamp,nonce
        String[] parts = headerValue.split(",");
        if (parts.length != 3) {
            throw new IllegalArgumentException("Invalid header format");
        }
        
        String signaturePart = parts[0];
        String timestampStr = parts[1];
        String nonce = parts[2];
        
        // Validate timestamp to prevent replay attacks
        long timestamp = Long.parseLong(timestampStr);
        long currentTime = System.currentTimeMillis() / 1000;
        if (Math.abs(currentTime - timestamp) > maxAgeSeconds) {
            throw new IllegalArgumentException("Signature timestamp is too old");
        }
        
        // Parse the signature to extract algorithm and value
        if (!signaturePart.contains("=")) {
            throw new IllegalArgumentException("Invalid signature format");
        }
        
        String[] signatureParts = signaturePart.split("=", 2);
        String algorithm = signatureParts[0];
        String signatureValue = signatureParts[1];
        
        // Convert payload to sorted JSON
        String jsonPayload = createSortedJson(payload);
        
        // Combine URL and payload as done in signature generation
        String signatureData = webhookUrl + "|" + jsonPayload;
        
        // Compute expected signature
        String expectedSignature = computeHmac(signatureData, apiToken, algorithm);
        
        // Compare signatures using timing-safe comparison
        return constantTimeEquals(expectedSignature, signatureValue);
    }
    
    private static String createSortedJson(Object payload) throws Exception {
        ObjectMapper mapper = new ObjectMapper();
        JsonNode node = mapper.valueToTree(payload);
        
        // Convert to sorted map
        Map<String, Object> sortedMap = new TreeMap<>();
        node.fields().forEachRemaining(entry -> {
            sortedMap.put(entry.getKey(), entry.getValue());
        });
        
        return mapper.writeValueAsString(sortedMap);
    }
    
    private static String computeHmac(String data, String key, String algorithm) 
            throws NoSuchAlgorithmException, InvalidKeyException {
        
        String hmacAlgorithm = "Hmac" + algorithm.toUpperCase();
        Mac mac = Mac.getInstance(hmacAlgorithm);
        SecretKeySpec secretKeySpec = new SecretKeySpec(
            key.getBytes(StandardCharsets.UTF_8), 
            hmacAlgorithm
        );
        mac.init(secretKeySpec);
        
        byte[] hash = mac.doFinal(data.getBytes(StandardCharsets.UTF_8));
        return bytesToHex(hash);
    }
    
    private static String bytesToHex(byte[] bytes) {
        StringBuilder result = new StringBuilder();
        for (byte b : bytes) {
            result.append(String.format("%02x", b));
        }
        return result.toString();
    }
    
    private static boolean constantTimeEquals(String a, String b) {
        if (a.length() != b.length()) {
            return false;
        }
        
        int result = 0;
        for (int i = 0; i < a.length(); i++) {
            result |= a.charAt(i) ^ b.charAt(i);
        }
        return result == 0;
    }
    
    // Example usage
    public static void main(String[] args) {
        try {
            Map<String, Object> payload = new HashMap<>();
            payload.put("domain", "example.com");
            payload.put("action", "created");
            
            String headerValue = "sha256=a1b2c3d4e5f6...,1640995200,550e8400-e29b-41d4-a716-446655440000"; // From X-NAMECOM-SIGNATURE header
            String apiToken = "your-api-token";
            String webhookUrl = "https://partner.example.com/webhook/domain-created"; // The exact full webhook subscription URL
            int maxAgeSeconds = 300;
            
            if (verifyHmacSignature(payload, headerValue, apiToken, webhookUrl, maxAgeSeconds)) {
                System.out.println("Signature is valid");
            } else {
                System.out.println("Signature is invalid");
            }
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        }
    }
}
```

### Ruby

```ruby theme={null}
require 'openssl'
require 'json'

def verify_hmac_signature(payload, header_value, api_token, webhook_url, max_age_seconds = 300)
  # Parse the header value: signature,timestamp,nonce
  parts = header_value.split(',')
  unless parts.length == 3
    raise ArgumentError, 'Invalid header format'
  end
  
  signature_part, timestamp_str, nonce = parts
  
  # Validate timestamp to prevent replay attacks
  timestamp = timestamp_str.to_i
  current_time = Time.now.to_i
  if (current_time - timestamp).abs > max_age_seconds
    raise ArgumentError, 'Signature timestamp is too old'
  end
  
  # Parse the signature to extract algorithm and value
  unless signature_part.include?('=')
    raise ArgumentError, 'Invalid signature format'
  end
  
  algorithm, signature_value = signature_part.split('=', 2)
  
  # Convert payload to hash and sort keys
  payload_hash = payload.is_a?(Hash) ? payload : payload.to_h
  sorted_payload = payload_hash.sort.to_h
  
  # JSON encode the sorted payload
  json_payload = JSON.generate(sorted_payload)
  
  # Combine URL and payload as done in signature generation
  signature_data = webhook_url + '|' + json_payload
  
  # Get the digest class based on algorithm
  digest_class = case algorithm
                 when 'sha256'
                   OpenSSL::Digest.new('sha256')
                 else
                   raise ArgumentError, "Unsupported algorithm: #{algorithm}"
                 end
  
  # Compute expected signature
  expected_signature = OpenSSL::HMAC.hexdigest(
    digest_class,
    api_token,
    signature_data
  )
  
  # Compare signatures using timing-safe comparison
  secure_compare(expected_signature, signature_value)
end

def secure_compare(a, b)
  return false if a.bytesize != b.bytesize
  
  result = 0
  a.bytes.zip(b.bytes) { |x, y| result |= x ^ y }
  result == 0
end

# Example usage
payload = { 'domain' => 'example.com', 'action' => 'created' }
header_value = 'sha256=a1b2c3d4e5f6...,1640995200,550e8400-e29b-41d4-a716-446655440000' # From X-NAMECOM-SIGNATURE header
api_token = 'your-api-token'
webhook_url = 'https://partner.example.com/webhook/domain-created' # The exact full webhook subscription URL

begin
  if verify_hmac_signature(payload, header_value, api_token, webhook_url)
    puts 'Signature is valid'
  else
    puts 'Signature is invalid'
  end
rescue => e
  puts "Error: #{e.message}"
end
```

## Important Notes

1. **Key Sorting**: The payload keys must be sorted alphabetically before JSON encoding to ensure consistent signature generation.

2. **JSON Encoding**: Use consistent JSON encoding settings across all implementations to match name.com's signature generation.

3. **URL Inclusion**: Use the exact full webhook subscription URL in the signature calculation (`<full_webhook_url>|<sorted_json_payload>`), not a path-only value.

4. **Timing-Safe Comparison**: Always use timing-safe comparison functions to prevent timing attacks when comparing signatures.

5. **Timestamp Validation**: The timestamp validation prevents replay attacks by rejecting signatures older than the specified time window (default 5 minutes).

6. **Nonce Usage**: While the nonce is included in the header for uniqueness, it's not used in signature verification but helps with request tracking and debugging.

7. **Error Handling**: Implement proper error handling for invalid header formats, timestamp validation failures, and unsupported algorithms.

8. **Character Encoding**: Ensure consistent UTF-8 encoding across all implementations.

9. **Algorithm Support**: The examples support dynamic algorithm detection from the signature header, allowing for future algorithm changes.

10. **Security**: The combination of HMAC signature (including full URL), timestamp validation, and nonce provides strong protection against replay attacks and cross-endpoint attacks while ensuring request authenticity.

11. **Testing**: Test with the same payload, API token, and webhook URL to ensure all implementations produce identical results.
