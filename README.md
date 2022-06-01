# ray-downscale-test

This sample KubeRay RayCluster configuration shows how the worker nodes are not downscaled when using `serve start --http-location EveryNode`

```sh
kind create cluster --name ray-test --config kind-config.yaml

kubectl create -k kuberay/
sleep 2
kubectl wait --for=condition=established crd/rayclusters.ray.io

kubectl -n ray-system apply -f raycluster-autoscaler.yaml
sleep 2
kubectl -n ray-system wait --for=condition=ready pod -l ray.io/identifier=raycluster-autoscaler-head

docker run -it --rm --net=host -v $(pwd):/app rayproject/ray:1.12.1 /app/run.sh
```
