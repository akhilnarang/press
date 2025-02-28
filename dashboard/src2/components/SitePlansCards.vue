<template>
	<div class="@container" v-if="plans.length">
		<div
			class="grid grid-cols-1 gap-3 @md:grid-cols-2 @2xl:grid-cols-3 @3xl:grid-cols-4"
		>
			<button
				v-for="(plan, i) in plans"
				:key="plan.name"
				class="flex flex-col overflow-hidden rounded border text-left hover:bg-gray-50"
				:class="[
					modelValue === plan.name
						? 'border-gray-900 ring-1 ring-gray-900'
						: 'border-gray-300',
					{
						'pointer-events-none': plan.disabled
					}
				]"
				@click="$emit('update:modelValue', plan.name)"
			>
				<div
					class="w-full border-b p-3"
					:class="[
						modelValue === plan.name
							? 'border-gray-900 ring-1 ring-gray-900'
							: ''
					]"
				>
					<div class="flex items-center justify-between">
						<div class="text-lg">
							<span class="font-medium text-gray-900">
								{{ $format.planTitle(plan) }}
							</span>
							<span v-if="plan.price_inr" class="text-gray-700"> /mo</span>
						</div>
					</div>
					<div class="mt-1 text-sm text-gray-600">
						{{
							$format.userCurrency(
								$format.pricePerDay(
									$team.doc.currency === 'INR' ? plan.price_inr : plan.price_usd
								)
							)
						}}
						/day
					</div>
				</div>
				<div class="p-3 text-p-sm text-gray-800">
					<div>
						<span>{{ plan.cpu_time_per_day }} </span>
						<span class="ml-1 text-gray-600">
							{{
								$format.plural(
									plan.cpu_time_per_day,
									'compute hour',
									'compute hours'
								)
							}}
							/ day
						</span>
					</div>
					<div>
						<span>
							{{ $format.bytes(plan.max_database_usage, 0, 2) }}
						</span>
						<span class="text-gray-600"> database </span>
					</div>
					<div>
						<span>
							{{ $format.bytes(plan.max_storage_usage, 0, 2) }}
						</span>
						<span class="text-gray-600"> disk </span>
					</div>
					<div v-if="plan.support_included">
						<span> Support Included </span>
					</div>
					<div v-if="plan.database_access">
						<span> Database Access </span>
					</div>
					<div v-if="plan.offsite_backups">
						<span> Offsite Backups </span>
					</div>
					<div v-if="plan.monitor_access">
						<span> Advanced Monitoring </span>
					</div>
				</div>
			</button>
		</div>
	</div>
</template>

<script>
import { Tabs } from 'frappe-ui';
import { getPlans } from '../data/plans';

export default {
	name: 'SitePlansCards',
	props: ['modelValue'],
	emits: ['update:modelValue'],
	components: {
		FTabs: Tabs
	},
	data() {
		return {
			currentTab: 0
		};
	},
	computed: {
		tabs() {
			return [
				{
					label: 'Basic',
					description:
						'Basic plan for small sites or testing purposes. Support is only available for Frappe Cloud hosting related questions and issues.',
					plans: this.plans.filter(p => !p.support_included)
				},
				{
					label: 'Support Included',
					description:
						'These plans include Frappe (OEM) Product Warranty for sites that have ERPNext, Frappe HR, and Frappe Framework apps installed.',
					plans: this.plans.filter(p => p.support_included)
				}
			];
		},
		plans() {
			return getPlans();
		}
	}
};
</script>
