'use client';

import { FormEvent, useEffect, useState } from 'react';
import { getStockComments, postStockComment, type StockComment } from '@/lib/api';

type Props = {
  symbol: string;
};

export function StockCommunity({ symbol }: Props) {
  const [items, setItems] = useState<StockComment[]>([]);
  const [nickname, setNickname] = useState('');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  async function loadComments() {
    const data = await getStockComments(symbol, 1, 20);
    setItems(data.items);
  }

  useEffect(() => {
    loadComments();
  }, [symbol]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!nickname.trim() || !content.trim()) {
      setMessage('닉네임과 내용을 입력해주세요.');
      return;
    }

    setLoading(true);
    setMessage('');
    const created = await postStockComment(symbol, nickname.trim(), content.trim());
    setLoading(false);

    if (!created) {
      setMessage('등록에 실패했습니다. 잠시 후 다시 시도해주세요.');
      return;
    }

    setNickname('');
    setContent('');
    setItems((prev) => [created, ...prev]);
    setMessage('의견이 등록되었습니다.');
  }

  return (
    <section className="mt-6 rounded-xl border border-zinc-800 bg-zinc-950 p-6">
      <h2 className="text-xl font-semibold">Community Notes</h2>
      <p className="mt-2 text-sm text-zinc-400">해당 기업에 대한 의견을 남기고 다른 사용자 인사이트를 확인하세요.</p>

      <form className="mt-4 space-y-3" onSubmit={onSubmit}>
        <input
          value={nickname}
          onChange={(e) => setNickname(e.target.value)}
          placeholder="닉네임"
          maxLength={40}
          className="w-full rounded border border-zinc-700 bg-black px-3 py-2 text-sm text-white placeholder:text-zinc-500"
        />
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="의견을 작성해 주세요"
          rows={4}
          maxLength={2000}
          className="w-full rounded border border-zinc-700 bg-black px-3 py-2 text-sm text-white placeholder:text-zinc-500"
        />
        <div className="flex items-center justify-between">
          <p className="text-xs text-zinc-500">{content.length}/2000</p>
          <button
            type="submit"
            disabled={loading}
            className="rounded border border-zinc-600 px-4 py-2 text-sm text-white transition hover:bg-zinc-900 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? '등록 중...' : '의견 등록'}
          </button>
        </div>
        {message ? <p className="text-sm text-zinc-400">{message}</p> : null}
      </form>

      <div className="mt-6 space-y-3">
        {items.length === 0 ? (
          <p className="text-sm text-zinc-400">아직 등록된 의견이 없습니다.</p>
        ) : (
          items.map((item) => (
            <article key={item.id} className="rounded-lg border border-zinc-800 bg-black p-3">
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm font-medium text-white">{item.nickname}</p>
                <p className="text-xs text-zinc-500">{new Date(item.created_at).toLocaleString()}</p>
              </div>
              <p className="mt-2 whitespace-pre-wrap text-sm text-zinc-300">{item.content}</p>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
