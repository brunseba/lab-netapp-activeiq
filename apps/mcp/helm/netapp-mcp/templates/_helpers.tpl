{{/*
Expand the name of the chart.
*/}}
{{- define "netapp-mcp-server.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "netapp-mcp-server.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "netapp-mcp-server.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "netapp-mcp-server.labels" -}}
helm.sh/chart: {{ include "netapp-mcp-server.chart" . }}
{{ include "netapp-mcp-server.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/component: mcp-server
app.kubernetes.io/part-of: netapp-integration
{{- end }}

{{/*
Selector labels
*/}}
{{- define "netapp-mcp-server.selectorLabels" -}}
app.kubernetes.io/name: {{ include "netapp-mcp-server.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Common annotations
*/}}
{{- define "netapp-mcp-server.annotations" -}}
meta.helm.sh/release-name: {{ .Release.Name }}
meta.helm.sh/release-namespace: {{ .Release.Namespace }}
deployment.kubernetes.io/revision: "{{ .Release.Revision }}"
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "netapp-mcp-server.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "netapp-mcp-server.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the secret to use
*/}}
{{- define "netapp-mcp-server.secretName" -}}
{{- if .Values.secret.name }}
{{- .Values.secret.name }}
{{- else }}
{{- printf "%s-credentials" (include "netapp-mcp-server.fullname" .) }}
{{- end }}
{{- end }}

{{/*
Create the name of the configmap to use
*/}}
{{- define "netapp-mcp-server.configMapName" -}}
{{- if .Values.configMap.name }}
{{- .Values.configMap.name }}
{{- else }}
{{- printf "%s-config" (include "netapp-mcp-server.fullname" .) }}
{{- end }}
{{- end }}

{{/*
Create the full image name
*/}}
{{- define "netapp-mcp-server.image" -}}
{{- $registry := .Values.image.registry }}
{{- if .Values.global.imageRegistry }}
{{- $registry = .Values.global.imageRegistry }}
{{- end }}
{{- if $registry }}
{{- printf "%s/%s:%s" $registry .Values.image.repository (.Values.image.tag | default .Chart.AppVersion) }}
{{- else }}
{{- printf "%s:%s" .Values.image.repository (.Values.image.tag | default .Chart.AppVersion) }}
{{- end }}
{{- end }}

{{/*
Create image pull secrets
*/}}
{{- define "netapp-mcp-server.imagePullSecrets" -}}
{{- $pullSecrets := list }}
{{- if .Values.global.imagePullSecrets }}
{{- $pullSecrets = concat $pullSecrets .Values.global.imagePullSecrets }}
{{- end }}
{{- if .Values.image.pullSecrets }}
{{- $pullSecrets = concat $pullSecrets .Values.image.pullSecrets }}
{{- end }}
{{- if $pullSecrets }}
imagePullSecrets:
{{- range $pullSecrets }}
- name: {{ . }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Validate NetApp configuration
*/}}
{{- define "netapp-mcp-server.validateNetApp" -}}
{{- if not .Values.netapp.existingSecret }}
{{- if or (not .Values.netapp.baseUrl) (not .Values.netapp.username) (not .Values.netapp.password) }}
{{- fail "NetApp configuration is required: baseUrl, username, and password must be provided or use existingSecret" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Get NetApp base URL
*/}}
{{- define "netapp-mcp-server.netappBaseUrl" -}}
{{- if .Values.netapp.existingSecret }}
{{- printf "secretKeyRef: {name: %s, key: %s}" .Values.netapp.existingSecret .Values.netapp.secretKeys.baseUrl }}
{{- else }}
{{- .Values.netapp.baseUrl }}
{{- end }}
{{- end }}

{{/*
Resource name validation
*/}}
{{- define "netapp-mcp-server.validateResourceName" -}}
{{- $name := include "netapp-mcp-server.fullname" . }}
{{- if gt (len $name) 63 }}
{{- fail (printf "Resource name '%s' is too long (max 63 characters)" $name) }}
{{- end }}
{{- end }}

{{/*
Validate Knative configuration
*/}}
{{- define "netapp-mcp-server.validateKnative" -}}
{{- if and .Values.knative.enabled .Values.ingress.enabled }}
{{- fail "Cannot enable both Knative Service and Ingress. Choose one deployment method." }}
{{- end }}
{{- end }}

{{/*
Generate environment variables for NetApp configuration
*/}}
{{- define "netapp-mcp-server.netappEnvVars" -}}
{{- if .Values.netapp.existingSecret }}
- name: NETAPP_BASE_URL
  valueFrom:
    secretKeyRef:
      name: {{ .Values.netapp.existingSecret }}
      key: {{ .Values.netapp.secretKeys.baseUrl }}
- name: NETAPP_USERNAME
  valueFrom:
    secretKeyRef:
      name: {{ .Values.netapp.existingSecret }}
      key: {{ .Values.netapp.secretKeys.username }}
- name: NETAPP_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ .Values.netapp.existingSecret }}
      key: {{ .Values.netapp.secretKeys.password }}
- name: NETAPP_VERIFY_SSL
  valueFrom:
    secretKeyRef:
      name: {{ .Values.netapp.existingSecret }}
      key: {{ .Values.netapp.secretKeys.verifySSL }}
- name: NETAPP_TIMEOUT
  valueFrom:
    secretKeyRef:
      name: {{ .Values.netapp.existingSecret }}
      key: {{ .Values.netapp.secretKeys.timeout }}
{{- else }}
- name: NETAPP_BASE_URL
  valueFrom:
    secretKeyRef:
      name: {{ include "netapp-mcp-server.secretName" . }}
      key: NETAPP_BASE_URL
- name: NETAPP_USERNAME
  valueFrom:
    secretKeyRef:
      name: {{ include "netapp-mcp-server.secretName" . }}
      key: NETAPP_USERNAME
- name: NETAPP_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ include "netapp-mcp-server.secretName" . }}
      key: NETAPP_PASSWORD
- name: NETAPP_VERIFY_SSL
  valueFrom:
    secretKeyRef:
      name: {{ include "netapp-mcp-server.secretName" . }}
      key: NETAPP_VERIFY_SSL
- name: NETAPP_TIMEOUT
  valueFrom:
    secretKeyRef:
      name: {{ include "netapp-mcp-server.secretName" . }}
      key: NETAPP_TIMEOUT
{{- end }}
{{- end }}

{{/*
Generate standard application environment variables
*/}}
{{- define "netapp-mcp-server.appEnvVars" -}}
- name: LOG_LEVEL
  value: {{ .Values.app.logLevel | quote }}
- name: SERVICE_NAME
  value: {{ .Values.app.serviceName | quote }}
- name: SERVICE_VERSION
  value: {{ .Values.app.serviceVersion | quote }}
- name: KUBERNETES_NAMESPACE
  valueFrom:
    fieldRef:
      fieldPath: metadata.namespace
- name: POD_NAME
  valueFrom:
    fieldRef:
      fieldPath: metadata.name
- name: NODE_NAME
  valueFrom:
    fieldRef:
      fieldPath: spec.nodeName
{{- range $key, $value := .Values.app.extraEnv }}
- name: {{ $key }}
  value: {{ $value | quote }}
{{- end }}
{{- end }}

{{/*
Generate monitoring labels
*/}}
{{- define "netapp-mcp-server.monitoringLabels" -}}
{{- if .Values.monitoring.serviceMonitor.enabled }}
monitoring: "true"
prometheus.io/scrape: "true"
prometheus.io/port: {{ .Values.container.port | quote }}
prometheus.io/path: {{ .Values.monitoring.serviceMonitor.path | quote }}
{{- end }}
{{- end }}

{{/*
Generate pod disruption budget name
*/}}
{{- define "netapp-mcp-server.pdbName" -}}
{{- printf "%s-pdb" (include "netapp-mcp-server.fullname" .) }}
{{- end }}

{{/*
Generate horizontal pod autoscaler name
*/}}
{{- define "netapp-mcp-server.hpaName" -}}
{{- printf "%s-hpa" (include "netapp-mcp-server.fullname" .) }}
{{- end }}

{{/*
Generate network policy name
*/}}
{{- define "netapp-mcp-server.networkPolicyName" -}}
{{- printf "%s-netpol" (include "netapp-mcp-server.fullname" .) }}
{{- end }}

{{/*
Generate service monitor name
*/}}
{{- define "netapp-mcp-server.serviceMonitorName" -}}
{{- printf "%s-servicemonitor" (include "netapp-mcp-server.fullname" .) }}
{{- end }}

{{/*
Capability check for Pod Security Standards
*/}}
{{- define "netapp-mcp-server.podSecurityStandards" -}}
{{- if .Capabilities.APIVersions.Has "policy/v1beta1/PodSecurityPolicy" }}
policy/v1beta1
{{- else if .Capabilities.APIVersions.Has "policy/v1/PodSecurityPolicy" }}
policy/v1
{{- else }}
""
{{- end }}
{{- end }}
