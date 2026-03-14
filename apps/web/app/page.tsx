import Link from 'next/link';
import { getHealth } from '@/lib/api';

const highlights = [
  {
    title: '멀티팩터 스코어링 모델',
    description:
      '퀄리티, 밸류, 성장, 수익성 지표를 표준화해 단일 점수로 통합하고 섹터/규모 편향을 최소화합니다.',
  },
  {
    title: '모멘텀·실적 리비전 모니터링',
    description:
      '가격 추세, 거래 강도, 이익추정치 변화를 함께 추적해 컨센서스 변화와 펀더멘털 모멘텀을 점검합니다.',
  },
  {
    title: '리스크 기반 후보군 관리',
    description:
      '변동성, 유동성, 낙폭 지표를 반영해 리스크 대비 기대수익 관점에서 우선 검토 종목을 제시합니다.',
  },
];

export default async function HomePage() {
  const health = await getHealth();

  return (
    <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10 lg:py-14">
      <section className="rounded-2xl border border-zinc-700 bg-black p-5 sm:p-7 md:p-10">
        <p className="text-[11px] uppercase tracking-[0.22em] text-zinc-400 sm:text-xs">Institutional Equity Research Console</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white sm:mt-4 sm:text-4xl md:text-5xl">
          기관 수준의 주식 리서치를 한 화면에서.
        </h1>
        <p className="mt-4 max-w-3xl text-sm leading-relaxed text-zinc-300 sm:mt-5 sm:text-base">
          WATS는 시점 일치(point-in-time) 데이터를 기반으로 종목 랭킹, 추천, 턴어라운드 후보를 제공합니다.
          모든 결과는 팩터 근거와 함께 제시되어 포트폴리오 의사결정의 투명성과 재현성을 높입니다.
        </p>

        <div className="mt-6 grid gap-3 sm:mt-8 sm:flex sm:flex-wrap">
          <Link
            href="/top-picks"
            className="w-full rounded-lg bg-white px-5 py-2.5 text-center text-sm font-semibold text-black transition hover:bg-zinc-200 sm:w-auto"
          >
            모델 추천 종목 보기
          </Link>
          <Link
            href="/about-methodology"
            className="w-full rounded-lg border border-zinc-600 px-5 py-2.5 text-center text-sm font-medium text-zinc-100 transition hover:bg-zinc-900 sm:w-auto"
          >
            리서치 방법론
          </Link>
        </div>
      </section>

      <section className="mt-5 grid gap-4 lg:mt-6 lg:grid-cols-[1fr_280px]">
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {highlights.map((item) => (
            <article key={item.title} className="rounded-xl border border-zinc-800 bg-zinc-950 p-5">
              <h2 className="text-sm font-semibold text-white">{item.title}</h2>
              <p className="mt-2 text-sm leading-relaxed text-zinc-400">{item.description}</p>
            </article>
          ))}
        </div>

        <aside className="rounded-xl border border-zinc-800 bg-zinc-950 p-5">
          <p className="text-xs font-medium uppercase tracking-[0.2em] text-zinc-500">Research System Status</p>
          <p className="mt-2 text-xl font-semibold text-white">{health?.status ?? 'unavailable'}</p>
          <p className="mt-2 text-sm text-zinc-400">데이터 수집·스코어링·추천 파이프라인의 현재 운영 상태를 나타냅니다.</p>
        </aside>
      </section>
    </main>
  );
}
