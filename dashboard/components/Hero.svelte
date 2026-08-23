<script>
	// Reusable AeroFlow hero header.
	// `page` is the short, page specific label shown above the wordmark
	// (for example "Home", "Airports" or "Routes").
	// `tagline` is the fixed brand line shown beneath the wordmark.
	export let page = '';
	export let tagline = 'Global Flight Network Analytics';
</script>

<header class="aeroflow-hero" aria-label="AeroFlow">
	<div class="aeroflow-hero__backdrop" aria-hidden="true">
		<div class="aeroflow-hero__grid"></div>
		<svg
			class="aeroflow-hero__arcs"
			viewBox="0 0 1200 260"
			preserveAspectRatio="none"
			xmlns="http://www.w3.org/2000/svg"
		>
			<defs>
				<linearGradient id="aeroflowArcStroke" x1="0" y1="0" x2="1" y2="0">
					<stop offset="0%" stop-color="#fb923c" />
					<stop offset="55%" stop-color="#fb923c" />
					<stop offset="100%" stop-color="#60a5fa" />
				</linearGradient>
			</defs>
			<path class="aeroflow-hero__arc aeroflow-hero__arc--1" d="M-40 208 Q 320 44 700 140 T 1240 74" />
			<path class="aeroflow-hero__arc aeroflow-hero__arc--2" d="M-40 92 Q 380 220 820 122 T 1240 182" />
			<path class="aeroflow-hero__arc aeroflow-hero__arc--3" d="M-40 250 Q 520 150 900 224 T 1240 150" />
		</svg>
	</div>

	{#if page}
		<p class="aeroflow-hero__eyebrow">{page}</p>
	{/if}
	<h1 class="aeroflow-hero__title">AeroFlow</h1>
	<div class="aeroflow-hero__bar" aria-hidden="true"></div>
	<p class="aeroflow-hero__tagline">{tagline}</p>
</header>

<style>
	.aeroflow-hero {
		position: relative;
		isolation: isolate;
		margin: 0.5rem 0 1.9rem;
		padding-top: 0.85rem;
	}

	/* ---- Faint animated backdrop: drifting tech grid + flight path arcs ---- */
	.aeroflow-hero__backdrop {
		position: absolute;
		inset: -1.35rem -0.75rem -0.6rem -0.75rem;
		z-index: -1;
		pointer-events: none;
		overflow: hidden;
	}

	.aeroflow-hero__grid {
		position: absolute;
		inset: 0;
		background-image:
			linear-gradient(to right, hsl(var(--twc-primary) / 0.9) 1px, transparent 1px),
			linear-gradient(to bottom, hsl(var(--twc-accent) / 0.9) 1px, transparent 1px);
		background-size: 46px 46px;
		opacity: 0.07;
		-webkit-mask-image: radial-gradient(120% 135% at 16% -12%, #000 0%, transparent 68%);
		mask-image: radial-gradient(120% 135% at 16% -12%, #000 0%, transparent 68%);
		animation: aeroflow-grid-drift 26s linear infinite;
	}

	.aeroflow-hero__arcs {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		opacity: 0.2;
	}

	.aeroflow-hero__arc {
		fill: none;
		stroke: url(#aeroflowArcStroke);
		stroke-width: 1.4;
		stroke-linecap: round;
		stroke-dasharray: 5 12;
		vector-effect: non-scaling-stroke;
		animation: aeroflow-arc-flow 3.6s linear infinite;
	}

	.aeroflow-hero__arc--2 {
		animation-duration: 5s;
		opacity: 0.8;
	}

	.aeroflow-hero__arc--3 {
		animation-duration: 6.6s;
		opacity: 0.6;
	}

	/* ---- Eyebrow: monospace geometric accent with a glowing marker ---- */
	.aeroflow-hero__eyebrow {
		display: inline-flex;
		align-items: center;
		margin: 0 0 0.6rem;
		font-family: var(--monospace-font-family, ui-monospace, monospace);
		font-size: 0.72rem;
		font-weight: 600;
		letter-spacing: 0.28em;
		text-transform: uppercase;
		color: hsl(var(--twc-accent));
	}

	.aeroflow-hero__eyebrow::before {
		content: '';
		display: inline-block;
		width: 0.5rem;
		height: 0.5rem;
		margin-right: 0.6rem;
		border-radius: 1px;
		background: hsl(var(--twc-primary));
		box-shadow: 0 0 7px hsl(var(--twc-primary) / 0.65);
	}

	/* ---- Wordmark: slow gradient shimmer sweeping orange into blue ---- */
	.aeroflow-hero__title {
		position: relative;
		margin: 0;
		font-weight: 800;
		line-height: 0.95;
		letter-spacing: -0.035em;
		font-size: clamp(2.75rem, 1.35rem + 5.6vw, 5.25rem);
		background-image: linear-gradient(
			100deg,
			hsl(var(--twc-primary)) 0%,
			hsl(var(--twc-primary)) 30%,
			hsl(var(--twc-accent)) 50%,
			hsl(var(--twc-primary)) 70%,
			hsl(var(--twc-primary)) 100%
		);
		background-size: 220% 100%;
		background-position: 120% 0;
		-webkit-background-clip: text;
		background-clip: text;
		color: transparent;
		-webkit-text-fill-color: transparent;
		filter: drop-shadow(0 2px 18px hsl(var(--twc-primary) / 0.28));
		animation: aeroflow-shimmer 7s ease-in-out infinite;
	}

	/* ---- Accent underline: gentle pulse and glow ---- */
	.aeroflow-hero__bar {
		width: clamp(3.75rem, 9vw, 6.5rem);
		height: 5px;
		margin: 1.05rem 0 0.95rem;
		border-radius: 999px;
		background: linear-gradient(90deg, hsl(var(--twc-primary)), hsl(var(--twc-accent)));
		animation: aeroflow-bar-pulse 3.4s ease-in-out infinite;
	}

	.aeroflow-hero__tagline {
		margin: 0;
		max-width: 44rem;
		font-size: clamp(1.02rem, 0.9rem + 0.55vw, 1.3rem);
		font-weight: 500;
		line-height: 1.5;
		color: hsl(var(--twc-base-content));
	}

	@keyframes aeroflow-shimmer {
		0% {
			background-position: 120% 0;
		}
		50% {
			background-position: -20% 0;
		}
		100% {
			background-position: 120% 0;
		}
	}

	@keyframes aeroflow-bar-pulse {
		0%,
		100% {
			box-shadow: 0 0 6px hsl(var(--twc-primary) / 0.35);
			opacity: 0.9;
		}
		50% {
			box-shadow:
				0 0 16px hsl(var(--twc-accent) / 0.55),
				0 0 6px hsl(var(--twc-primary) / 0.45);
			opacity: 1;
		}
	}

	@keyframes aeroflow-grid-drift {
		from {
			background-position:
				0 0,
				0 0;
		}
		to {
			background-position:
				46px 46px,
				46px 46px;
		}
	}

	@keyframes aeroflow-arc-flow {
		to {
			stroke-dashoffset: -34;
		}
	}

	@media (max-width: 640px) {
		.aeroflow-hero {
			margin-top: 0.25rem;
		}
	}

	/* Respect users who prefer reduced motion: hold every animation still
	   while keeping the wordmark gradient and accents fully legible. */
	@media (prefers-reduced-motion: reduce) {
		.aeroflow-hero__title,
		.aeroflow-hero__bar,
		.aeroflow-hero__grid,
		.aeroflow-hero__arc {
			animation: none !important;
		}

		.aeroflow-hero__title {
			background-position: 0 0;
		}
	}
</style>
