import {
  AbsoluteFill,
  Easing,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { z } from "zod";
import { PITCH_SLIDES, type PitchSlide } from "./pitchDeckData";

export const pitchDeckSchema = z.object({
  tagline: z.string(),
  website: z.string(),
  raiseTarget: z.string(),
});

export type PitchDeckProps = z.infer<typeof pitchDeckSchema>;

export const PITCH_DECK_FPS = 30;
export const PITCH_DECK_WIDTH = 1920;
export const PITCH_DECK_HEIGHT = 1080;
export const PITCH_DECK_SCENE_DURATION_IN_FRAMES = 150;
const TRANSITION_DURATION_IN_FRAMES = 18;

export const PITCH_DECK_DURATION_IN_FRAMES =
  PITCH_SLIDES.length * PITCH_DECK_SCENE_DURATION_IN_FRAMES -
  (PITCH_SLIDES.length - 1) * TRANSITION_DURATION_IN_FRAMES;

const PALETTES = [
  {
    bgTop: "#041327",
    bgBottom: "#071a2e",
    accent: "#4fd1c5",
    accentSoft: "rgba(79, 209, 197, 0.22)",
    ring: "rgba(107, 241, 229, 0.24)",
  },
  {
    bgTop: "#1b1230",
    bgBottom: "#291334",
    accent: "#ffa94d",
    accentSoft: "rgba(255, 169, 77, 0.2)",
    ring: "rgba(255, 200, 136, 0.24)",
  },
  {
    bgTop: "#0e1e2f",
    bgBottom: "#112a3a",
    accent: "#7dd3fc",
    accentSoft: "rgba(125, 211, 252, 0.2)",
    ring: "rgba(176, 232, 255, 0.24)",
  },
  {
    bgTop: "#1f1324",
    bgBottom: "#2d1b30",
    accent: "#fca5a5",
    accentSoft: "rgba(252, 165, 165, 0.2)",
    ring: "rgba(254, 207, 207, 0.25)",
  },
] as const;

const COVER_SNIPPET = [
  "# SOCIAL.md",
  "## Project",
  'name: "FastCache"',
  'tagline: "In-memory caching that just works"',
  "",
  "## Channels",
  "- twitter",
  "- hackernews",
  "- dev.to",
  "",
  "## Launch Tasks",
  "- [ ] Write announcement",
  "- [ ] Post demo",
] as const;

const PREMOUNT_IN_FRAMES = PITCH_DECK_FPS;

export const PitchDeck: React.FC<PitchDeckProps> = ({
  tagline,
  website,
  raiseTarget,
}) => {
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: "#030814" }}>
      {PITCH_SLIDES.map((slide, index) => (
        <Sequence
          key={slide.title}
          from={index * (PITCH_DECK_SCENE_DURATION_IN_FRAMES - TRANSITION_DURATION_IN_FRAMES)}
          durationInFrames={PITCH_DECK_SCENE_DURATION_IN_FRAMES}
          premountFor={PREMOUNT_IN_FRAMES || fps}
        >
          <PitchDeckScene
            slide={slide}
            index={index}
            total={PITCH_SLIDES.length}
            tagline={tagline}
            website={website}
            raiseTarget={raiseTarget}
          />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

type PitchDeckSceneProps = {
  readonly slide: PitchSlide;
  readonly index: number;
  readonly total: number;
  readonly tagline: string;
  readonly website: string;
  readonly raiseTarget: string;
};

const PitchDeckScene: React.FC<PitchDeckSceneProps> = ({
  slide,
  index,
  total,
  tagline,
  website,
  raiseTarget,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const palette = PALETTES[index % PALETTES.length];
  const isCover = index === 0;
  const isAsk = slide.title.toLowerCase() === "ask";

  const sceneIn = spring({
    frame: frame - 2,
    fps,
    config: { damping: 200 },
  });

  const sceneOut = spring({
    frame:
      frame -
      (PITCH_DECK_SCENE_DURATION_IN_FRAMES - TRANSITION_DURATION_IN_FRAMES),
    fps,
    config: { damping: 200 },
  });

  const enterX = interpolate(sceneIn, [0, 1], [80, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const exitY = interpolate(sceneOut, [0, 1], [0, -34], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.quad),
  });

  const opacity = interpolate(
    frame,
    [0, 8, PITCH_DECK_SCENE_DURATION_IN_FRAMES - 14, PITCH_DECK_SCENE_DURATION_IN_FRAMES],
    [0, 1, 1, 0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    },
  );

  const driftA = Math.sin((frame + index * 13) / 16) * 28;
  const driftB = Math.cos((frame + index * 11) / 19) * 24;
  const progress = interpolate(frame, [0, PITCH_DECK_SCENE_DURATION_IN_FRAMES], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const headline = slide.bullets[0] ?? "";
  const revealEnd = Math.min(
    PITCH_DECK_SCENE_DURATION_IN_FRAMES - 36,
    Math.max(Math.floor(2.1 * fps), Math.floor(headline.length * 0.9)),
  );
  const typedChars = Math.floor(
    interpolate(frame, [8, revealEnd], [0, headline.length], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }),
  );
  const renderedHeadline = isCover ? headline.slice(0, typedChars) : headline;

  const sectionBullets = slide.bullets.slice(1, 6);
  const askSignals = isAsk
    ? [
        slide.bullets.find((line) => line.toLowerCase().startsWith("raise amount")) ??
          `Raise amount: ${raiseTarget}`,
        slide.bullets.find((line) => line.toLowerCase().startsWith("runway target")) ??
          "Runway target: 18 months",
      ]
    : [];

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at 18% 18%, ${palette.accentSoft}, transparent 40%), linear-gradient(160deg, ${palette.bgTop} 0%, ${palette.bgBottom} 100%)`,
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute",
          width: 520,
          height: 520,
          borderRadius: "50%",
          border: `1px solid ${palette.ring}`,
          left: -150,
          top: -170,
          transform: `translate(${driftA}px, ${driftB}px)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          width: 700,
          height: 700,
          borderRadius: "50%",
          border: `1px solid ${palette.ring}`,
          right: -220,
          bottom: -290,
          transform: `translate(${-driftB}px, ${driftA}px)`,
        }}
      />

      <div
        style={{
          position: "absolute",
          inset: 0,
          padding: "74px 84px 64px",
          opacity,
          transform: `translate3d(${enterX}px, ${exitY}px, 0)`,
          display: "flex",
          flexDirection: "column",
          gap: 24,
          color: "#f7fbff",
          fontFamily: '"Avenir Next", "Trebuchet MS", "Segoe UI", sans-serif',
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 18,
          }}
        >
          <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
            <div
              style={{
                fontFamily: '"Courier New", monospace',
                fontSize: 17,
                letterSpacing: 1.4,
                textTransform: "uppercase",
                color: palette.accent,
              }}
            >
              {String(index + 1).padStart(2, "0")} / {String(total).padStart(2, "0")}
            </div>
            <div
              style={{
                padding: "7px 12px",
                borderRadius: 999,
                fontSize: 14,
                fontWeight: 600,
                backgroundColor: "rgba(255,255,255,0.08)",
              }}
            >
              SOCIAL.md investor narrative
            </div>
          </div>
          <div
            style={{
              fontSize: 16,
              fontWeight: 600,
              color: "rgba(247, 251, 255, 0.86)",
            }}
          >
            {website}
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <h1
            style={{
              margin: 0,
              fontSize: isCover ? 80 : 66,
              lineHeight: 1,
              letterSpacing: -1.6,
              fontWeight: 800,
              fontFamily: '"Gill Sans Nova", "Avenir Next Condensed", "Trebuchet MS", sans-serif',
            }}
          >
            {slide.title}
          </h1>
          <div
            style={{
              fontSize: isCover ? 41 : 34,
              lineHeight: 1.23,
              maxWidth: isCover ? 1400 : 1320,
              color: "rgba(247, 251, 255, 0.95)",
              minHeight: isCover ? 140 : 90,
            }}
          >
            {renderedHeadline}
          </div>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: isCover ? "1.18fr 0.82fr" : "1fr 1fr",
            gap: 26,
            marginTop: 8,
            flex: 1,
          }}
        >
          <div
            style={{
              borderRadius: 24,
              padding: "26px 28px",
              background: "rgba(8, 17, 33, 0.56)",
              border: `1px solid ${palette.ring}`,
              display: "flex",
              flexDirection: "column",
              gap: 14,
            }}
          >
            {(sectionBullets.length > 0 ? sectionBullets : slide.bullets.slice(0, 5)).map(
              (bullet, bulletIndex) => (
                <AnimatedBullet
                  key={`${slide.title}-${bullet}`}
                  bullet={bullet}
                  index={bulletIndex}
                  accent={palette.accent}
                  sceneFrame={frame}
                />
              ),
            )}
          </div>

          {isCover ? (
            <CoverPanel accent={palette.accent} tagline={tagline} />
          ) : isAsk ? (
            <AskPanel accent={palette.accent} signals={askSignals} />
          ) : (
            <FocusPanel
              accent={palette.accent}
              title={slide.title}
              bullets={slide.bullets.slice(0, 4)}
            />
          )}
        </div>

        <div
          style={{
            marginTop: "auto",
            height: 6,
            borderRadius: 999,
            backgroundColor: "rgba(255,255,255,0.18)",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              width: `${Math.round(progress * 100)}%`,
              height: "100%",
              borderRadius: 999,
              backgroundColor: palette.accent,
            }}
          />
        </div>
      </div>
    </AbsoluteFill>
  );
};

type AnimatedBulletProps = {
  readonly bullet: string;
  readonly index: number;
  readonly accent: string;
  readonly sceneFrame: number;
};

const AnimatedBullet: React.FC<AnimatedBulletProps> = ({
  bullet,
  index,
  accent,
  sceneFrame,
}) => {
  const start = 28 + index * 11;
  const opacity = interpolate(sceneFrame, [start, start + 8], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const x = interpolate(sceneFrame, [start, start + 8], [30, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <div
      style={{
        opacity,
        transform: `translateX(${x}px)`,
        display: "flex",
        alignItems: "flex-start",
        gap: 12,
      }}
    >
      <div
        style={{
          width: 9,
          height: 9,
          marginTop: 10,
          flexShrink: 0,
          borderRadius: 999,
          backgroundColor: accent,
          boxShadow: `0 0 18px ${accent}`,
        }}
      />
      <div
        style={{
          fontSize: 25,
          lineHeight: 1.33,
          color: "rgba(247, 251, 255, 0.92)",
        }}
      >
        {bullet}
      </div>
    </div>
  );
};

const CoverPanel: React.FC<{ readonly accent: string; readonly tagline: string }> = ({
  accent,
  tagline,
}) => {
  return (
    <div
      style={{
        borderRadius: 24,
        padding: "20px 22px",
        background: "rgba(8, 17, 33, 0.66)",
        border: "1px solid rgba(255,255,255,0.2)",
        display: "flex",
        flexDirection: "column",
        gap: 16,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          color: "rgba(247,251,255,0.85)",
          fontFamily: '"Courier New", monospace',
          fontSize: 14,
          letterSpacing: 1,
          textTransform: "uppercase",
        }}
      >
        <span
          style={{
            width: 8,
            height: 8,
            borderRadius: 999,
            backgroundColor: accent,
            boxShadow: `0 0 16px ${accent}`,
          }}
        />
        Launch Manifest Preview
      </div>
      <div
        style={{
          fontSize: 20,
          fontWeight: 600,
          lineHeight: 1.35,
          color: "rgba(247,251,255,0.95)",
        }}
      >
        {tagline}
      </div>
      <div
        style={{
          borderRadius: 14,
          border: "1px solid rgba(255,255,255,0.2)",
          padding: "14px 16px",
          backgroundColor: "rgba(2, 7, 18, 0.75)",
          color: "rgba(218, 231, 247, 0.95)",
          fontSize: 14,
          fontFamily: '"Courier New", monospace',
          lineHeight: 1.45,
          whiteSpace: "pre-wrap",
          flex: 1,
        }}
      >
        {COVER_SNIPPET.join("\n")}
      </div>
    </div>
  );
};

const FocusPanel: React.FC<{
  readonly accent: string;
  readonly title: string;
  readonly bullets: readonly string[];
}> = ({ accent, title, bullets }) => {
  return (
    <div
      style={{
        borderRadius: 24,
        padding: "24px 24px",
        background: "rgba(8, 17, 33, 0.66)",
        border: "1px solid rgba(255,255,255,0.2)",
        display: "flex",
        flexDirection: "column",
        gap: 14,
      }}
    >
      <div
        style={{
          fontSize: 14,
          fontFamily: '"Courier New", monospace',
          letterSpacing: 1,
          textTransform: "uppercase",
          color: accent,
        }}
      >
        Pivot question
      </div>
      <div
        style={{
          fontSize: 36,
          lineHeight: 1.15,
          fontWeight: 700,
          letterSpacing: -0.7,
          color: "#f7fbff",
        }}
      >
        {title}
      </div>
      <div
        style={{
          borderTop: "1px solid rgba(255,255,255,0.18)",
          paddingTop: 14,
          display: "flex",
          flexDirection: "column",
          gap: 10,
        }}
      >
        {bullets.map((line) => (
          <div
            key={`${title}-${line}`}
            style={{
              fontSize: 20,
              lineHeight: 1.32,
              color: "rgba(247, 251, 255, 0.9)",
            }}
          >
            {line}
          </div>
        ))}
      </div>
    </div>
  );
};

const AskPanel: React.FC<{
  readonly accent: string;
  readonly signals: readonly string[];
}> = ({ accent, signals }) => {
  return (
    <div
      style={{
        borderRadius: 24,
        padding: "24px 24px",
        background: "rgba(8, 17, 33, 0.66)",
        border: "1px solid rgba(255,255,255,0.2)",
        display: "flex",
        flexDirection: "column",
        gap: 14,
      }}
    >
      <div
        style={{
          fontSize: 14,
          fontFamily: '"Courier New", monospace',
          letterSpacing: 1,
          textTransform: "uppercase",
          color: accent,
        }}
      >
        Funding target
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 12,
        }}
      >
        {signals.map((signal) => (
          <div
            key={signal}
            style={{
              border: `1px solid ${accent}`,
              borderRadius: 14,
              padding: "14px 12px",
              backgroundColor: "rgba(255,255,255,0.05)",
              fontSize: 20,
              lineHeight: 1.32,
              fontWeight: 700,
              color: "#f7fbff",
            }}
          >
            {signal}
          </div>
        ))}
      </div>
      <div
        style={{
          marginTop: 6,
          fontSize: 18,
          lineHeight: 1.4,
          color: "rgba(247, 251, 255, 0.9)",
        }}
      >
        Use this round to validate repeatable launch outcomes, sharpen retention, and convert design-partner results into seed-ready proof.
      </div>
    </div>
  );
};
