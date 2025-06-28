<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# retrieve me thi openapi file of it

NetApp Active IQ Unified Manager exposes its REST API definition via an embedded **Swagger/OpenAPI** interface, but NetApp does **not publish a downloadable OpenAPI (Swagger) YAML or JSON file directly on their public documentation sites**. Instead, the OpenAPI definition is served dynamically from your own Unified Manager instance.

### How to Retrieve the OpenAPI (Swagger) File

1. **Access the API Documentation (Swagger UI):**
    - Open your browser and go to:

```
https://<Unified_Manager_IP_or_FQDN>/apidocs/
```

    - Example:

```
https://10.10.10.10/apidocs/
```

    - You must have Operator, Storage Administrator, or Application Administrator role to access[^1][^2][^3][^4].
2. **Download the OpenAPI Definition:**
    - In the Swagger UI, look for an "Export" or "Download" button (typically available in recent versions).
    - If there is no direct button, you can:
        - Open your browser's developer tools (F12), go to the "Network" tab, and reload the page.
        - Look for a request ending in `/swagger.json` or `/openapi.json`.
        - Right-click that request and choose "Open in new tab" or "Save as...", then save the file.
3. **Alternative:**
    - If your version does not provide a direct download, you can manually copy the JSON content from the `/swagger.json` or `/openapi.json` endpoint and save it as a `.json` file.

### Notes

- The OpenAPI file you retrieve will reflect the version and capabilities of your specific Unified Manager instance.
- There is no static, vendor-hosted OpenAPI file available for direct download from NetApp’s public documentation[^5][^1][^6][^2][^3][^4].
- The API documentation is always up-to-date with your deployed product version.

**Summary:**
To obtain the OpenAPI file for ActiveIQ NetApp REST API, access the Swagger UI at `https://<your-unified-manager>/apidocs/` on your instance and export or retrieve the OpenAPI JSON from there[^1][^2][^3][^4].

<div style="text-align: center">⁂</div>

[^1]: https://docs.netapp.com/us-en/active-iq-unified-manager-98/reporting/generaltask-um-rest-apis-that-can-be-used-for-reporting.html

[^2]: https://docs.netapp.com/us-en/active-iq-unified-manager-914/reporting/generaltask_um_rest_apis_that_can_be_used_for_reporting.html

[^3]: https://github.com/NetAppDocs/oncommand-unified-manager-95/blob/main/health-checker/task-accessing-rest-apis-using-the-swagger-api-web-page-ocum.adoc

[^4]: https://docs.netapp.com/us-en/active-iq-unified-manager-97/api-automation/concept-api-url-and-categories.html

[^5]: https://docs.netapp.com/us-en/active-iq-unified-manager/api-automation/concept_get_started_with_um_apis.html

[^6]: https://docs.netapp.com/us-en/active-iq-unified-manager-97/api-automation/concept-getting-started-with-getting-started-with-um-apis.html

[^7]: https://docs.netapp.com/fr-fr/active-iq-unified-manager-912/storage-mgmt/concept_use_unified_manager_rest_apis_ocum.html

[^8]: https://docs.netapp.com/fr-fr/active-iq-unified-manager/api-automation/concept_rest_api_access_and_authentication_in_um_apis.html

[^9]: https://docs.netapp.com/fr-fr/active-iq-unified-manager-911/api-automation/concept_hello_api_server.html

[^10]: https://docs.netapp.com/us-en/active-iq-unified-manager/api-automation/concept_rest_api_access_and_authentication_in_um_apis.html

[^11]: https://github.com/NetAppDocs/active-iq-unified-manager/blob/main/reporting/generaltask_um_rest_apis_that_can_be_used_for_reporting.adoc

[^12]: https://docs.netapp.com/us-en/netapp-automation/api/aiqum.html

[^13]: https://docs.netapp.com/us-en/active-iq/concept_overview_API_service.html

[^14]: https://github.com/NetAppDocs/active-iq-unified-manager-99/blob/main/api-automation/concept-gateway-apis.adoc

[^15]: https://www.netapp.com/blog/discover-active-iq-api-services/

[^16]: https://library.netapp.com/ecmdocs/ECMLP2582762/html/GUID-05D02C13-3650-45A7-9845-1E81587B65F4.html

[^17]: https://kb.netapp.com/@api/deki/pages/7950/pdf/API+Services+to+Unified+Manager+9.7+REST+API+mapping.pdf?stylesheet=default

[^18]: https://community.netapp.com/t5/Active-IQ-Unified-Manager-Discussions/Swagger-file-export-from-WFA/m-p/140934

[^19]: https://github.com/NetApp/Active-IQ-Unified-Manager

[^20]: https://github.com/NetAppDocs/active-iq-unified-manager/blob/main/config/concept_api_gateway.adoc

[^21]: https://docs.netapp.com/fr-fr/active-iq-unified-manager/api-automation/concept_rest_api_versioning_in_unified_manager_apis.html

[^22]: https://community.netapp.com/t5/Active-IQ-and-AutoSupport-Discussions/Issues-found-in-Active-IQ-Unified-Manager-REST-API-behavior/m-p/166752

[^23]: https://community.netapp.com/t5/Tech-ONTAP-Blogs/Active-IQ-Unified-Manager-9-9-Feature-Blog-User-Experience-Enhancements/ba-p/167555

