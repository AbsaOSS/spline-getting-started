#!/bin/bash
NS=spline
API=
UI=

# API=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath="{.*.loadBalancer.ingress[*].hostname}")
# UI=$(kubectl get svc -n ingress-nginx ingress-nginx-extra-controller -o jsonpath="{.*.loadBalancer.ingress[*].hostname}")

# ARANGODB-OPERATOR
# https://www.arangodb.com/docs/stable/deployment-kubernetes-usage.html
ARANGO_VERSION=1.2.8

URLPREFIX=https://github.com/arangodb/kube-arangodb/releases/download/$ARANGO_VERSION

## ArangoDB CRD
helm upgrade --install \
    kube-arangodb-crd $URLPREFIX/kube-arangodb-crd-$ARANGO_VERSION.tgz \

## ArangoDB Operator
helm upgrade --install kube-arangodb $URLPREFIX/kube-arangodb-$ARANGO_VERSION.tgz \
    --set operator.replicaCount=1 \
    -n $NS --create-namespace 

# ArangoDB cluster
ARANGO_PASSWORD=MySuperStrongPassword

helm upgrade --install arangodb arangodb \
    --set auth.password=$ARANGO_PASSWORD \
    --set tls.caSecretName=None \
    -n $NS

# SPLINE-ADMIN for initdb
helm upgrade --install \
    spline-admin spline-admin \
    --set arango.url="arangodb://root:$ARANGO_PASSWORD@arangodb:8529" \
    -n $NS

# Spline REST API
helm upgrade --install spline spline \
    --set arango.url="arangodb://root:$ARANGO_PASSWORD@arangodb:8529" \
    --set ingress.enabled="true" \
    --set ingress.host="$API" \
    --set ingress.ingressClass="nginx" \
    -n $NS

# API=$(kubectl get svc -n $NS spline -o jsonpath="{.*.loadBalancer.ingress[*].hostname}")

# SPLINE UI
helm upgrade --install spline-ui spline-ui \
    --set splineConsumerUrl="http://$API/consumer" \
    --set ingress.enabled="true" \
    --set ingress.host="$UI" \
    --set ingress.ingressClass="ingress" \
    -n $NS
