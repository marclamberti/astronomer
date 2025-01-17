from tests.helm_template_generator import render_chart
import pytest
from . import supported_k8s_versions


@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
class TestStanStatefulSet:
    def test_stan_statefulset_defaults(self, kube_version):
        """Test that stan statefulset is good with defaults."""
        docs = render_chart(
            kube_version=kube_version,
            show_only=["charts/stan/templates/statefulset.yaml"],
        )

        assert len(docs) == 1
        doc = docs[0]
        c_by_name = {
            c["name"]: c for c in doc["spec"]["template"]["spec"]["containers"]
        }
        assert doc["kind"] == "StatefulSet"
        assert doc["apiVersion"] == "apps/v1"
        assert doc["metadata"]["name"] == "RELEASE-NAME-stan"
        assert c_by_name["metrics"]["image"].startswith(
            "quay.io/astronomer/ap-nats-exporter:"
        )
        assert c_by_name["stan"]["image"].startswith(
            "quay.io/astronomer/ap-nats-streaming:"
        )
        assert c_by_name["stan"]["livenessProbe"] == {
            "httpGet": {"path": "/streaming/serverz", "port": "monitor"},
            "initialDelaySeconds": 10,
            "timeoutSeconds": 5,
        }
        assert c_by_name["stan"]["readinessProbe"] == {
            "httpGet": {"path": "/streaming/serverz", "port": "monitor"},
            "initialDelaySeconds": 10,
            "timeoutSeconds": 5,
        }

    def test_stan_statefulset_with_metrics_and_resources(self, kube_version):
        """Test that stan statefulset renders good metrics exporter."""
        docs = render_chart(
            kube_version=kube_version,
            show_only=["charts/stan/templates/statefulset.yaml"],
            values={
                "stan": {
                    "exporter": {
                        "enabled": True,
                        "resources": {"requests": {"cpu": "234m"}},
                    },
                    "stan": {"resources": {"requests": {"cpu": "123m"}}},
                },
            },
        )

        assert len(docs) == 1
        containers = docs[0]["spec"]["template"]["spec"]["containers"]
        assert len(containers) == 2
        c_by_name = {c["name"]: c for c in containers}
        assert c_by_name["stan"]["resources"]["requests"]["cpu"] == "123m"
        assert c_by_name["metrics"]["resources"]["requests"]["cpu"] == "234m"
