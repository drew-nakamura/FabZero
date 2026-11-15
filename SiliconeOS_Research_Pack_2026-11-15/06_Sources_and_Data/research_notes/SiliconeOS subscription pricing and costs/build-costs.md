# Build costs: condensed research notes

Checked November14,2026. Read-only customer_channel_research used official AMD/Microsoft sources. No cloud installation/job, device action or account transaction occurred. Local-runner orchestration is a costing assumption: the customer owning hardware does not determine where compilation runs.

## Local software orchestration changes who pays compute

For local Vivado builds, OUR cloud CPU bill is zero; the customer still supplies its machine, electricity, disk/RAM, tool eligibility and actual board/accessories. We retain compatibility maintenance, backend/storage and support costs.

[AMD2025.2 supported devices](https://docs.amd.com/r/2025.2-English/ug973-vivado-release-notes-install-license/Supported-Devices) include Kria in Standard without a license. [Current licensing](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/vivado/vivado-licensing-options.html) shows Linux AND Windows in free BASIC and Kria support; an earlier Windows-only search lead was superseded by the current table. CORE is listed at US$1,200 node-locked/US$1,800 floating annually, only where applicable. [FAQ](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/licensing-faq.html) distinguishes pre2026 Standard from annually renewed free BASIC licensing and separately licensed IP/evaluation restrictions. No blanket cloud-hosting/redistribution entitlement was established.

[AMD board-flow documentation, UG9942025.2](https://docs.amd.com/r/2025.2-English/ug994-vivado-ip-subsystems/Using-the-Platform-Board-Flow-in-IP-Integrator) relies on board/interface/preset/pin data. A sensor's name alone does not settle electrical, pin, clock/reset, protocol, driver or test integration. Subscription support should cover a tested versioned catalogue; unfamiliar combinations need separate qualification/engineering quotes.

## Optional hosted CPU examples

[Microsoft's exact retail query](https://prices.azure.com/api/retail/prices?%24filter=serviceName%20eq%20%27Virtual%20Machines%27%20and%20armRegionName%20eq%20%27eastus%27%20and%20%28armSkuName%20eq%20%27Standard_E8s_v5%27%20or%20armSkuName%20eq%20%27Standard_E16s_v5%27%29&currencyCode=USD) returned primary-meter Consumption USD East US Linux E8s_v5 US$0.504/hour and E16s_v5 US$1.008/hour, non-Spot. Corresponding Windows rates were US$0.872/US$1.744. Effective-start date2021-11-01, current retrieval2026-11-14. [Specifications](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/memory-optimized/esv5-series?tabs=sizebasic) give8vCPU/64GiB and16vCPU/128GiB, no FPGA or local temporary storage; attached disks cost extra.

Unmeasured scenario:20requests x2fresh variants x1hour x1.25attempts =50worker-hours, or US$25.20/US$50.40 CPU monthly. A15-minute attempt costs US$0.126/US$0.252. An allocated idle730-hour worker costs US$367.92/US$735.84 monthly. These are not measured build durations or service quotes. Cloud output still needs local physical programming/validation.

[Blob retail query](https://prices.azure.com/api/retail/prices?%24filter=serviceName%20eq%20%27Storage%27%20and%20armRegionName%20eq%20%27eastus%27%20and%20productName%20eq%20%27General%20Block%20Blob%20v2%27%20and%20skuName%20eq%20%27Hot%20LRS%27&currencyCode=USD) returned Hot LRS US$0.0208/GB-month:20GB costs US$0.416 before operations/transfers. [Managed-disk query](https://prices.azure.com/api/retail/prices?%24filter=serviceName%20eq%20%27Storage%27%20and%20armRegionName%20eq%20%27eastus%27%20and%20productName%20eq%20%27Premium%20SSD%20Managed%20Disks%27%20and%20skuName%20eq%20%27P15%20LRS%27&currencyCode=USD) returned P15 LRS US$38.012142/month with other meters present. Do not combine only CPU and blob and call that an all-in hosted service.

## Allocation assumptions, not quotes

A sharedUS$50-200/month backend budget allocatesUS$0.50-2 at100paying accounts, orUS$5-20 at10. Twenty to100GB basic blob storage isUS$0.42-2.08. Ten support minutes at a placeholderUS$60 internal hour costUS$10; an hour costsUS$60. No actual scale, retention, support distribution, loaded labor cost or license allocation was measured. Validated cache hits avoid fresh build cost; compile-time parameter changes can require distinct bitstreams. Finite retries/timeouts and queues bound cost without changing correctness checks.
