# vubernetes
Kubernetes Visualizer

- [vubernetes](#vubernetes)
  - [Overview](#overview)
  - [Examples](#examples)
    - [bookinfo.yaml](#bookinfoyaml)
      - [Product Page](#product-page)
      - [Detail](#detail)
      - [Reviews](#reviews)
      - [Ratings](#ratings)
    - [grafana.yaml](#grafanayaml)

## Overview

Still under development

Vubernetes takes in a `.yaml` Kubernetes manifest and generates `.png` files for each app and their allocated resources

## Examples

### bookinfo.yaml

`bookinfo.yaml` is created by the developers at Istio as a sample application. It consists of 4 different microservices:

1. Product Page: The `productpage` microservice calls the `details` and `reviews` microservices to populate the page.
2. Detail: The `details` microservice contains book information.
3. Reviews: The `reviews` microservice contains book reviews. It also calls the `ratings` microservice.
    - There are 3 versions of the `reviews` microservice
      1. Doesn’t call the ratings service.
      2. Calls the ratings service, and displays each rating as 1 to 5 black stars.
      3. Calls the ratings service, and displays each rating as 1 to 5 red stars.
4. Ratings: The `ratings` microservice contains book ranking information that accompanies a book review.

Running Vubernetes on `bookinfo.yaml` results in the following images being generated:

#### Product Page
![productpage](/output/bookinfo_graphs/productpage.png)
#### Detail
![detail](/output/bookinfo_graphs/details.png)
#### Reviews
![reviews](/output/bookinfo_graphs/reviews.png)
#### Ratings
![ratings](/output/bookinfo_graphs/ratings.png)

### grafana.yaml

`grafana.yaml` is created by the developers at Grafana labs as a manifest to quickly deploy a Grafana dashboard.

Running Vubernetes on `grafana.yaml` results in the following image:

![grafana](/output/grafana_graphs/grafana.png)
