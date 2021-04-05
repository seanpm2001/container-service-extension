# container-service-extension
# Copyright (c) 2020 VMware, Inc. All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause

import container_service_extension.operation_context as ctx
from container_service_extension.server_constants import CseOperation as CseOperationInfo  # noqa: E501
from container_service_extension.server_constants import K8S_PROVIDER_KEY
from container_service_extension.shared_constants import CSE_PAGINATION_DEFAULT_PAGE_SIZE  # noqa: E501
from container_service_extension.shared_constants import CSE_PAGINATION_FIRST_PAGE_NUMBER  # noqa: E501
from container_service_extension.shared_constants import PaginationKey
from container_service_extension.shared_constants import RequestKey
from container_service_extension.telemetry.constants import CseOperation
from container_service_extension.telemetry.telemetry_handler import \
    record_user_action_telemetry
import container_service_extension.utils as utils
from container_service_extension.vcdbroker import VcdBroker


@record_user_action_telemetry(cse_operation=CseOperation.CLUSTER_CREATE)
def cluster_create(request_data, op_ctx: ctx.OperationContext):
    """Request handler for cluster create operation.

    Required data: org_name, ovdc_name, cluster_name
    Conditional data and default values:
            network_name, num_nodes=2, num_cpu=None, mb_memory=None,
            storage_profile_name=None, template_name=default,
            template_revision=default, ssh_key=None, enable_nfs=False,
            rollback=True

    (data validation handled in broker)

    :return: Dict
    """
    vcd_broker = VcdBroker(op_ctx)
    return vcd_broker.create_cluster(data=request_data)


@record_user_action_telemetry(cse_operation=CseOperation.CLUSTER_RESIZE)
def cluster_resize(request_data, op_ctx: ctx.OperationContext):
    """Request handler for cluster resize operation.

    Required data: cluster_name, num_nodes
    Optional data and default values: org_name=None, ovdc_name=None
    Conditional data and default values:
            network_name, rollback=True

    (data validation handled in broker)

    :return: Dict
    """
    vcd_broker = VcdBroker(op_ctx)
    return vcd_broker.resize_cluster(data=request_data)


@record_user_action_telemetry(cse_operation=CseOperation.CLUSTER_DELETE)
def cluster_delete(request_data, op_ctx: ctx.OperationContext):
    """Request handler for cluster delete operation.

    Required data: cluster_name
    Optional data and default values: org_name=None, ovdc_name=None

    (data validation handled in broker)

    :return: Dict
    """
    vcd_broker = VcdBroker(op_ctx)
    return vcd_broker.delete_cluster(data=request_data)


@record_user_action_telemetry(cse_operation=CseOperation.CLUSTER_INFO)
def cluster_info(request_data, op_ctx: ctx.OperationContext):
    """Request handler for cluster info operation.

    Required data: cluster_name
    Optional data and default values: org_name=None, ovdc_name=None

    (data validation handled in broker)

    :return: Dict
    """
    vcd_broker = VcdBroker(op_ctx)
    return vcd_broker.get_cluster_info(data=request_data)


@record_user_action_telemetry(cse_operation=CseOperation.CLUSTER_CONFIG)
def cluster_config(request_data, op_ctx: ctx.OperationContext):
    """Request handler for cluster config operation.

    Required data: cluster_name
    Optional data and default values: org_name=None, ovdc_name=None

    (data validation handled in broker)

    :return: Dict
    """
    vcd_broker = VcdBroker(op_ctx)
    return vcd_broker.get_cluster_config(data=request_data)


@record_user_action_telemetry(cse_operation=CseOperation.CLUSTER_UPGRADE_PLAN)
def cluster_upgrade_plan(request_data, op_ctx: ctx.OperationContext):
    """Request handler for cluster upgrade-plan operation.

    data validation handled in broker

    :return: List[Tuple(str, str)]
    """
    vcd_broker = VcdBroker(op_ctx)
    return vcd_broker.get_cluster_upgrade_plan(data=request_data)


@record_user_action_telemetry(cse_operation=CseOperation.CLUSTER_UPGRADE)
def cluster_upgrade(request_data, op_ctx: ctx.OperationContext):
    """Request handler for cluster upgrade operation.

    data validation handled in broker

    :return: Dict
    """
    vcd_broker = VcdBroker(op_ctx)
    return vcd_broker.upgrade_cluster(data=request_data)


def _retain_cluster_list_common_properties(cluster_list: list, properties_to_retain: list = None) -> list:  # noqa: E501
    if properties_to_retain is None:
        properties_to_retain = []
    result = []
    for cluster_info in cluster_list:
        filtered_cluster_info = \
            {k: cluster_info.get(k) for k in properties_to_retain}
        result.append(filtered_cluster_info)
    return result


# TODO: Record telemetry in a different telemetry handler
@record_user_action_telemetry(cse_operation=CseOperation.CLUSTER_LIST)
def native_cluster_list(request_data, op_ctx: ctx.OperationContext):
    """Request handler for cluster list operation.

    Optional data and default values: org_name=None, ovdc_name=None

    (data validation handled in broker)

    :return: List
    """
    vcd_broker = VcdBroker(op_ctx)
    page_number = int(request_data.get(PaginationKey.PAGE_NUMBER, CSE_PAGINATION_FIRST_PAGE_NUMBER))  # noqa: E501
    page_size = int(request_data.get(PaginationKey.PAGE_SIZE, CSE_PAGINATION_DEFAULT_PAGE_SIZE))  # noqa: E501

    vcd_clusters_info = vcd_broker.get_clusters_by_page(data=request_data,
                                                        page_number=page_number,  # noqa: E501
                                                        page_size=page_size)
    properties_to_retain = [
        'name',
        'vdc',
        'status',
        'org_name',
        'k8s_version',
        K8S_PROVIDER_KEY
    ]
    clusters = vcd_clusters_info[PaginationKey.VALUES]
    result = _retain_cluster_list_common_properties(clusters,
                                                    properties_to_retain)

    # Extract the query params
    query_keys = [RequestKey.ORG_NAME, RequestKey.OVDC_NAME]
    query_params = {k: request_data[k] for k in query_keys if request_data.get(k) is not None}  # noqa: E501

    base_url = f"{op_ctx.client.get_api_uri().strip('/')}" \
               f"{CseOperationInfo.NATIVE_CLUSTER_LIST.api_path_format}"
    return utils.create_links_and_construct_paginated_result(
        base_url, result,
        vcd_clusters_info[PaginationKey.RESULT_TOTAL],
        page_number=page_number,
        page_size=page_size,
        query_params=query_params)


@record_user_action_telemetry(cse_operation=CseOperation.CLUSTER_LIST)
def cluster_list(request_data, op_ctx: ctx.OperationContext):
    """Request handler for cluster list operation.

    Optional data and default values: org_name=None, ovdc_name=None

    (data validation handled in broker)

    :return: List
    """
    vcd_broker = VcdBroker(op_ctx)

    vcd_clusters_info = vcd_broker.list_clusters(data=request_data)

    properties_to_retain = [
        'name',
        'vdc',
        'status',
        'org_name',
        'k8s_version',
        K8S_PROVIDER_KEY
    ]

    return _retain_cluster_list_common_properties(vcd_clusters_info,
                                                  properties_to_retain)


@record_user_action_telemetry(cse_operation=CseOperation.NODE_CREATE)
def node_create(request_data, op_ctx: ctx.OperationContext):
    """Request handler for node create operation.

    Required data: cluster_name, network_name
    Optional data and default values: org_name=None, ovdc_name=None,
        num_nodes=1, num_cpu=None, mb_memory=None, storage_profile_name=None,
        template_name=default, template_revision=default,
        ssh_key=None, rollback=True, enable_nfs=False,

    (data validation handled in broker)

    :return: Dict
    """
    vcd_broker = VcdBroker(op_ctx)
    return vcd_broker.create_nodes(data=request_data)


@record_user_action_telemetry(cse_operation=CseOperation.NODE_DELETE)
def node_delete(request_data, op_ctx: ctx.OperationContext):
    """Request handler for node delete operation.

    Required data: cluster_name, node_names_list
    Optional data and default values: org_name=None, ovdc_name=None

    (data validation handled in broker)

    :return: Dict
    """
    vcd_broker = VcdBroker(op_ctx)
    return vcd_broker.delete_nodes(data=request_data)


@record_user_action_telemetry(cse_operation=CseOperation.NODE_INFO)
def node_info(request_data, op_ctx: ctx.OperationContext):
    """Request handler for node info operation.

    Required data: cluster_name, node_name
    Optional data and default values: org_name=None, ovdc_name=None

    (data validation handled in broker)

    :return: Dict
    """
    vcd_broker = VcdBroker(op_ctx)
    return vcd_broker.get_node_info(data=request_data)