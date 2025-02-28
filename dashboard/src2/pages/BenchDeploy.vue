<template>
	<div class="p-5" v-if="deploy">
		<Button :route="{ name: `${object.doctype} Detail Deploys` }">
			<template #prefix>
				<i-lucide-arrow-left class="inline-block h-4 w-4" />
			</template>
			All deploys
		</Button>

		<div class="mt-3">
			<div class="flex w-full items-center">
				<h2 class="text-lg font-medium text-gray-900">{{ deploy.name }}</h2>
				<Badge class="ml-2" :label="deploy.status" />
				<Button
					class="ml-auto"
					@click="$resources.deploy.reload()"
					:loading="$resources.deploy.loading"
				>
					<template #icon>
						<i-lucide-refresh-ccw class="h-4 w-4" />
					</template>
				</Button>
			</div>
			<div>
				<div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
					<div>
						<div class="text-sm font-medium text-gray-500">Creation</div>
						<div class="mt-2 text-sm text-gray-900">
							{{ $format.date(deploy.creation) }}
						</div>
					</div>
					<div>
						<div class="text-sm font-medium text-gray-500">Creator</div>
						<div class="mt-2 text-sm text-gray-900">
							{{ deploy.owner }}
						</div>
					</div>
					<div>
						<div class="text-sm font-medium text-gray-500">Duration</div>
						<div class="mt-2 text-sm text-gray-900">
							{{
								deploy.build_end ? $format.duration(deploy.build_duration) : ''
							}}
						</div>
					</div>
					<div>
						<div class="text-sm font-medium text-gray-500">Start</div>
						<div class="mt-2 text-sm text-gray-900">
							{{ $format.date(deploy.build_start, 'llll') }}
						</div>
					</div>
					<div>
						<div class="text-sm font-medium text-gray-500">End</div>
						<div class="mt-2 text-sm text-gray-900">
							{{ $format.date(deploy.build_end, 'llll') }}
						</div>
					</div>
				</div>
			</div>
		</div>

		<div class="mt-8 space-y-4">
			<JobStep
				v-for="step in deploy.build_steps"
				:step="step"
				:key="step.name"
			/>
		</div>
	</div>
</template>
<script>
import { getCachedDocumentResource } from 'frappe-ui';
import { getObject } from '../objects';
import JobStep from '../components/JobStep.vue';

export default {
	name: 'BenchDeploy',
	props: ['id', 'objectType'],
	components: {
		JobStep
	},
	resources: {
		deploy() {
			return {
				type: 'document',
				doctype: 'Deploy Candidate',
				name: this.id,
				transform(deploy) {
					for (let step of deploy.build_steps) {
						if (step.status === 'Running') {
							step.isOpen = true;
						}
						step.title = `${step.stage} - ${step.step}`;
						step.output =
							step.command || step.output
								? `${step.command || ''}\n${step.output || ''}`.trim()
								: '';
						step.duration = ['Success', 'Failure'].includes(step.status)
							? step.cached
								? 'Cached'
								: `${step.duration}s`
							: null;
					}
					return deploy;
				}
			};
		}
	},
	mounted() {
		this.$socket.on(`bench_deploy:${this.id}:steps`, data => {
			if (data.name === this.id && this.$resources.deploy.doc) {
				this.$resources.deploy.reload();
			}
		});
		this.$socket.on(`bench_deploy:${this.id}:finished`, () => {
			let rgDoc = getCachedDocumentResource(
				'Release Group',
				this.$resources.deploy.doc.group
			);
			this.$resources.deploy.reload();
			rgDoc.reload();
		});
	},
	beforeUnmount() {
		this.$socket.off(`bench_deploy:${this.id}:steps`);
	},
	computed: {
		deploy() {
			return this.$resources.deploy.doc;
		},
		object() {
			return getObject(this.objectType);
		}
	}
};
</script>
