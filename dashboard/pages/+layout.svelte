<script>
	import '@evidence-dev/tailwind/fonts.css';
	import '../app.css';
	import { EvidenceDefaultLayout } from '@evidence-dev/core-components';
	export let data;
</script>

<EvidenceDefaultLayout
	{data}
	lightLogo="/aeroflow-logo-light.svg"
	darkLogo="/aeroflow-logo-dark.svg"
	homePageName="Home"
	builtWithEvidence={false}
>
	<slot slot="content" />
</EvidenceDefaultLayout>
