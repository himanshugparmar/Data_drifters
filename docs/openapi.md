**Updated Documentation Content:**

---

# API Documentation

## Overview

This document outlines the changes made to the API, specifically the removal of the `modulus` method and its associated parameters, responses, and error codes. This update is crucial for all stakeholders to ensure seamless integration and to avoid any disruptions in service.

## Endpoints

### Modified Endpoints

The following endpoints have been updated due to the removal of the `modulus` method:

- `/calculate`
- `/operations`
- `/results`

**Note:** Please refer to the specific endpoint documentation below for detailed changes.

## Parameters

### Changes in Parameters

Parameters specifically associated with the `modulus` method have been removed. Clients are advised to review their API calls to these endpoints to ensure compliance with the new parameter requirements.

## Responses

### Updated Response Objects

Response objects and types that previously depended on the output of the `modulus` method have been revised. The API will no longer provide modulus calculation results in the responses. Clients should adjust their data handling accordingly.

## Error Codes

### Revision of Error Codes

Error codes specifically related to the `modulus` method (e.g., `Error 501: Modulus Method Not Supported`) have been removed from our documentation and API responses. Please review the updated error handling section for guidance on the new error codes.

## Examples

### Updated Examples

All examples demonstrating the usage of the `modulus` method have been removed or updated to reflect the current capabilities of the API. Below is an updated example for the `/calculate` endpoint:

**Previous Example:**
```json
{
  "operation": "modulus",
  "operands": [10, 3]
}
```

**Updated Example:**
```json
{
  "operation": "addition",
  "operands": [10, 3]
}
```

## Conclusion

The removal of the `modulus` method is part of our ongoing efforts to streamline our services and provide more robust solutions. We appreciate your understanding and cooperation in making the necessary adjustments to your API integrations. For further assistance, please contact our support team.

--- 

**Note:** This documentation update is effective immediately, and all stakeholders are encouraged to review the changes in detail to ensure full compliance and optimal use of the API.