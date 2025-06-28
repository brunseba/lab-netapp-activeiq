<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# Le fichier OpenAPI est-il disponible en téléchargement via Swagger ou autre plateforme

Le fichier OpenAPI (Swagger) de l’API REST d’Active IQ Unified Manager **n’est pas disponible en téléchargement direct sur une plateforme publique ou via le site NetApp**. Cependant, il est bien **fourni avec l’instance installée** d’Active IQ Unified Manager, accessible via l’interface Swagger intégrée au produit.

### Où et comment accéder au fichier OpenAPI ?

- **Depuis l’interface web de Unified Manager** :
Connectez-vous à votre instance Unified Manager, puis :
    - Cliquez sur le bouton **Aide** (Help) dans la barre de menu.
    - Sélectionnez **API Documentation**.
Cela ouvre la page Swagger, qui documente toutes les routes REST disponibles[^1][^2][^3][^4].
- **Accès direct par URL** :
Vous pouvez accéder à la documentation Swagger directement à l’adresse :

```
https://<adresse_IP_ou_FQDN>/docs/api/
```

ou parfois :

```
https://<adresse_IP_ou_FQDN>/apidocs/
```

(Remplacez `<adresse_IP_ou_FQDN>` par l’adresse de votre serveur Unified Manager)[^2][^4].
- **Téléchargement du fichier OpenAPI** :
    - Sur la page Swagger, il peut y avoir un bouton pour exporter ou télécharger la spécification (JSON ou YAML).
    - Sinon, via les outils de développement de votre navigateur (F12), recherchez la requête vers `/swagger.json` ou `/openapi.json`, ouvrez-la dans un nouvel onglet et sauvegardez le contenu.


### Points importants

- **Accès restreint** : Il faut avoir un rôle d’Operator, Storage Administrator ou Application Administrator pour accéder à la documentation API[^1][^3].
- **Pas de dépôt public** : NetApp ne publie pas ce fichier sur GitHub ou une autre plateforme publique. Il est généré dynamiquement par votre instance Unified Manager et reflète la version installée[^1][^2].
- **Mise à jour automatique** : La documentation Swagger est toujours à jour avec la version de votre produit.

**En résumé :**
Le fichier OpenAPI de l’API REST Active IQ Unified Manager est accessible et exportable via l’interface Swagger intégrée à votre instance, mais n’est pas disponible en téléchargement public sur Internet. Vous devez passer par votre installation pour l’obtenir[^1][^2][^3][^4].

<div style="text-align: center">⁂</div>

[^1]: https://github.com/NetAppDocs/active-iq-unified-manager/blob/main/reporting/generaltask_um_rest_apis_that_can_be_used_for_reporting.adoc

[^2]: https://docs.netapp.com/us-en/active-iq-unified-manager/api-automation/concept_api_url_and_categories.html

[^3]: https://storage-system.fujitsu.com/manual/en/active-iq-unified-manager/reporting/generaltask_um_rest_apis_that_can_be_used_for_reporting.html

[^4]: https://storage-system.fujitsu.com/manual/en/active-iq-unified-manager-913/api-automation/concept_api_url_and_categories.html

[^5]: https://github.com/NetAppDocs/active-iq-unified-manager-99/blob/main/api-automation/concept-rest-api-access-and-authentication-in-oncommand-api-services.adoc

[^6]: https://docs-snaplogic.atlassian.net/wiki/spaces/SD/pages/356876298/Viewing+Pipeline+APIs+in+Swagger+Alpha+Version?showComments=true\&showCommentArea=true

[^7]: https://docs.netapp.com/us-en/active-iq-unified-manager/api-automation/concept_get_started_with_um_apis.html

[^8]: https://swagger.io/tools/swagger-ui/

[^9]: https://docs.netapp.com/fr-fr/active-iq-unified-manager/api-automation/concept_rest_api_versioning_in_unified_manager_apis.html

[^10]: https://community.netapp.com/t5/Active-IQ-Unified-Manager-Discussions/Swagger-file-export-from-WFA/m-p/140934

[^11]: https://community.netapp.com/t5/Active-IQ-and-AutoSupport-Discussions/Active-IQ-API-and-swagger-client/m-p/160351

[^12]: https://swagger.io/tools/swagger-editor/download/

[^13]: https://docs.netapp.com/us-en/active-iq-unified-manager/install-linux/task_download_unified_manager.html

[^14]: https://github.com/NetAppDocs/active-iq-unified-manager/blob/main/config/concept_api_gateway.adoc

[^15]: https://docs.opsramp.com/integrations/storage-management/netapp-activeiq/

[^16]: https://mysupport.netapp.com/site/products/all/details/activeiq-unified-manager/downloads-tab

[^17]: https://storage-system.fujitsu.com/manual/en/active-iq-unified-manager/storage-mgmt/task_export_storage_data_as_reports.html

[^18]: https://library.netapp.com/ecmdocs/ECMLP2582762/html/GUID-05D02C13-3650-45A7-9845-1E81587B65F4.html

[^19]: https://storage-system.fujitsu.com/manual/en/active-iq-unified-manager/api-automation/concept_api_url_and_categories.html

