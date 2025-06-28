<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# searching about ActiveIQ netapp rest/api definition

NetApp ActiveIQ provides a robust REST API suite—primarily through **Active IQ Unified Manager** and **Digital Advisor**—to programmatically manage, monitor, and extract data from NetApp storage environments.

## Overview of ActiveIQ REST API

- **RESTful Design:** The APIs follow REST principles, supporting standard HTTP methods (GET, POST, PATCH, DELETE) for full CRUD operations on storage resources[^1][^2].
- **Coverage:** Over 100 endpoints grouped into 20+ service areas, covering system information, storage efficiency, performance, health, upgrades, and more[^3].
- **Use Cases:** Automate monitoring, integrate with ticketing/reporting systems, build dashboards, and manage storage resources.


## API Access and Authentication

- **Endpoint Structure:**
Example for clusters:

```
GET https://<hostname>:<port>/api/v2/datacenter/cluster/clusters
```

    - Default port: 443 (HTTPS)[^2][^4].
- **Authentication:**
    - Uses HTTP Basic Authentication (username/password).
    - Secure access via HTTPS, with support for self-signed or custom SSL certificates[^2][^4].
    - Both local and LDAP users are supported for API access management.


## API Catalog and Documentation

- **API Catalog:**
    - Browse and test APIs interactively via the Digital Advisor API Catalog, which provides code samples and a "try it out" browser experience[^3].
    - Endpoints are organized by service area and include code view (input/output details) and experiment view (live testing)[^3].
- **Sample Request/Response:**

```http
GET https://<hostname>:443/api/v2/datacenter/cluster/clusters
```

**Sample Response:**

```json
{
  "records": [
    {
      "key": "4c6bf721-2e3f-11e9-a3e2-00a0985badbb:type=cluster,uuid=4c6bf721-2e3f-11e9-a3e2-00a0985badbb",
      "name": "fas8040-206-21",
      "uuid": "4c6bf721-2e3f-11e9-a3e2-00a0985badbb",
      "version": {
        "full": "NetApp Release Dayblazer__9.5.0: Thu Jan 17 10:28:33 UTC 2019"
      },
      "management_ip": "10.226.207.25",
      "nodes": [
        {
          "uuid": "12cf06cc-2e3a-11e9-b9b4-00a0985badbb",
          "name": "fas8040-206-21-01",
          "model": "FAS8040"
        }
      ]
    }
  ]
}
```


## Development and Automation

- **Clients:** Any REST client or programming language (e.g., Python, Perl, Java, cURL) can interact with the API[^2][^5].
- **Automation:** APIs are designed for integration into automation workflows, enabling tasks like health checks, risk detection, and data extraction to be scripted and scheduled[^3].


## Resources

- **Official Documentation:**
    - [Active IQ Unified Manager API Automation](https://docs.netapp.com/us-en/active-iq-unified-manager/api-automation/concept_get_started_with_um_apis.html)[^1]
    - [Digital Advisor API Services](https://docs.netapp.com/us-en/active-iq/concept_overview_API_service.html)[^3]
    - [REST API Access and Authentication](https://docs.netapp.com/us-en/active-iq-unified-manager/api-automation/concept_rest_api_access_and_authentication_in_um_apis.html)[^2]

**In summary:**
ActiveIQ NetApp REST APIs offer secure, comprehensive, and well-documented endpoints for managing and monitoring NetApp storage resources. They are accessible via HTTPS with basic authentication, and can be integrated into any automation or monitoring toolchain using standard REST principles[^1][^3][^2][^4][^5].

<div style="text-align: center">⁂</div>

[^1]: https://docs.netapp.com/us-en/active-iq-unified-manager/api-automation/concept_get_started_with_um_apis.html

[^2]: https://docs.netapp.com/us-en/active-iq-unified-manager/api-automation/concept_rest_api_access_and_authentication_in_um_apis.html

[^3]: https://docs.netapp.com/us-en/active-iq/concept_overview_API_service.html

[^4]: https://github.com/NetAppDocs/active-iq-unified-manager-99/blob/main/api-automation/concept-rest-api-access-and-authentication-in-oncommand-api-services.adoc

[^5]: https://docs.netapp.com/fr-fr/active-iq-unified-manager-911/api-automation/concept_hello_api_server.html

[^6]: https://docs.netapp.com/fr-fr/active-iq-unified-manager-912/storage-mgmt/concept_use_unified_manager_rest_apis_ocum.html

[^7]: https://docs.netapp.com/us-en/ontap-automation/reference/api_reference.html

[^8]: https://github.com/NetAppDocs/active-iq/blob/master/concept_overview_API_service.adoc

[^9]: https://www.youtube.com/watch?v=Ov13phwH394

[^10]: https://docs.netapp.com/us-en/active-iq-unified-manager-912/api-automation/concept_rest_api_access_and_authentication_in_um_apis.html

