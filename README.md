
# Knative-DAPR-GPU-K8s

## Overview

This project demonstrates how to run GPU-powered machine learning workloads on Kubernetes using Knative and DAPR. By leveraging **NVIDIA GPUs** in **Google Kubernetes Engine (GKE)**, you can dynamically scale AI inference services with **Knative** while managing state and inter-service communication through **DAPR**. This architecture is optimized for both real-time and batch processing workloads.

In this project, we deploy a scalable pipeline that includes the following services:
- **Preprocessing**: Cleans and transforms input data.
- **Inference**: Performs ML inference using GPU resources (e.g., Llama2 model with NVIDIA A100 GPUs).
- **Postprocessing**: Handles the storage and caching of results.

The system is secured with **Istio**, utilizing mTLS for secure service-to-service communication, and is configured to autoscale based on demand.

## Architecture Components

- **Kubernetes (GKE)**: Manages the containerized workloads.
- **Knative Serving**: Provides serverless, autoscaling functionality for the services.
- **DAPR (Distributed Application Runtime)**: Manages service-to-service communication, pub/sub, and state management.
- **NVIDIA GPUs**: Used for accelerating machine learning inference workloads.
- **Istio**: Provides secure networking between services within the mesh using mutual TLS.
- **Redis**: Acts as an in-memory cache for fast access to inference results.
- **PostgreSQL**: Provides long-term storage for processed data.

## Prerequisites

- **Google Cloud SDK (gcloud)**
- **A Google Cloud Project** with Kubernetes Engine API enabled.
- **Access to NVIDIA GPUs** in GKE.

## Setup

### 1. List Available Accelerators

To begin, check the available GPU accelerator types in your Google Cloud project:

```bash
gcloud compute accelerator-types list --project $PROJECT_ID
```

This will display the available GPU types in various regions, such as **NVIDIA Tesla A100**, which is used in this project.

### 2. Create a GPU Node Pool in GKE

To provision GPU resources, create a new node pool in your existing GKE cluster with NVIDIA GPUs:

```bash
gcloud container node-pools create knative-dapr-gpu-node \
    --project phx-01had7ny8p --cluster=cluster-1 --zone us-east1-b \
    --machine-type a2-highgpu-1g --num-nodes 1 \
    --accelerator type=nvidia-tesla-a100,count=1,gpu-driver-version=default,gpu-partition-size=1g.5gb \
    --enable-autoupgrade
```

This command provisions a **GKE node pool** with **NVIDIA Tesla A100** GPUs, enabling the cluster to handle AI/ML inference workloads. 

### 3. Install Knative

To install Knative Serving on your Kubernetes cluster, follow these steps:

#### Install Knative CRDs:

```bash
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.0.0/serving-crds.yaml
```

#### Install Knative Core Components:

```bash
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.0.0/serving-core.yaml
```

Verify the Knative Serving installation by checking if the pods are running:

```bash
kubectl get pods -n knative-serving
```

### 4. Install DAPR

To install DAPR on your Kubernetes cluster:

#### Initialize DAPR in your Kubernetes cluster:

```bash
dapr init --kubernetes
```

#### Verify DAPR installation:

```bash
kubectl get pods -n dapr-system
```

This will show the running DAPR components in the `dapr-system` namespace.

### 5. Deploy Services to Kubernetes

In this project, we define three main services: **Preprocess**, **Inference**, and **Postprocess**, each running in the `ollama` namespace. These services are deployed as Knative services, utilizing DAPR for state management and Redis/PostgreSQL for caching and persistence.

- **Preprocess Service**: Cleans and prepares input data before sending it to the inference service.
- **Inference Service**: Performs machine learning inference using the Llama2 model running on NVIDIA GPUs.
- **Postprocess Service**: Stores results in Redis and PostgreSQL for both short- and long-term storage.

### 6. Service Configuration

#### Preprocess Service:

The **Preprocess Service** handles the initial data transformation.

Key environment variables:
- `REDIS_HOST`: Hostname of the Redis service for caching preprocessed data.

#### Inference Service:

The **Inference Service** performs GPU-accelerated inference using the Llama2 model.

Key environment variables:
- `GPU_ENABLED`: Set to "true" to enable GPU utilization.
- `OLLAMA_HOST`: The address of the Ollama inference service.

#### Postprocess Service:

The **Postprocess Service** stores the inference results in Redis and PostgreSQL for both short- and long-term storage.

Key environment variables:
- `REDIS_HOST`: Hostname of the Redis service for caching.
- `PG_HOST`: Hostname of the PostgreSQL service for persistent storage.

### 7. Configure Istio for Secure Networking

Istio is used to manage secure communication between services using **mTLS** (mutual TLS). A **VirtualService** is configured to route external traffic through the **Istio Ingress Gateway**, directing it to the appropriate Knative services (preprocess, inference, postprocess).

Example Istio **VirtualService** configuration:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ollama
  namespace: ollama
spec:
  gateways:
    - istio-ingress/mesh-gateway
  hosts:
    - "ollama.<your-ip>.nip.io"
  http:
    - match:
        - uri:
            prefix: "/preprocess"
      route:
        - destination:
            host: preprocess-service.ollama.svc.cluster.local
            port:
              number: 80
    - match:
        - uri:
            prefix: "/inference"
      route:
        - destination:
            host: inference-service.ollama.svc.cluster.local
            port:
              number: 80
    - match:
        - uri:
            prefix: "/postprocess"
      route:
        - destination:
            host: postprocess-service.ollama.svc.cluster.local
            port:
              number: 80
```

### 8. Autoscaling and Resource Management

Knative automatically scales the services based on incoming traffic, adjusting the number of pods dynamically. For example, the **Inference Service** is autoscaled based on GPU utilization and traffic load, with the ability to scale from 1 to 5 pods depending on demand.

Example autoscaling configuration in Knative:
```yaml
autoscaling.knative.dev/target: "2"  # Target 2 concurrent requests per pod
autoscaling.knative.dev/minScale: "1" # Minimum number of pods
autoscaling.knative.dev/maxScale: "5" # Maximum number of pods
```

### 9. Security and Best Practices

- **Non-root containers**: All services are configured to run as **non-root users** with restricted Linux capabilities, enhancing security.
- **mTLS (mutual TLS)**: Istio ensures encrypted and authenticated communication between services.

### 10. Cleanup

To delete the resources created in this project, run the following command:

```bash
gcloud container clusters delete cluster-1 --zone us-east1-b
```

This command deletes the entire GKE cluster, including the node pools and deployed services.

## Conclusion

This project demonstrates how to efficiently run GPU-powered AI workloads in Kubernetes using Knative and DAPR. By leveraging cloud-native technologies, you can dynamically scale services, handle stateful workloads, and manage secure communication between services, all while utilizing powerful NVIDIA GPUs for inference.
