'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

type ReviewChoice = 'a' | 'b' | 'tie';
type ReviewStage = 0 | 1 | 2 | 3;

type ReviewRow = {
  version: 2;
  id: string;
  lineage_id: string;
  input_method: string;
  input: string;
  response_a: string;
  response_b: string;
  factuality_a_pass?: boolean | null;
  factuality_b_pass?: boolean | null;
  unsupported_claims_a?: string[];
  unsupported_claims_b?: string[];
  instruction_following_a_pass?: boolean | null;
  instruction_following_b_pass?: boolean | null;
  voice_preference?: ReviewChoice | null;
  overall_preference?: ReviewChoice | null;
  edit_burden_a?: number | null;
  edit_burden_b?: number | null;
  notes?: string | null;
};

type WritableFile = {
  write(data: Blob | string): Promise<void>;
  close(): Promise<void>;
};

type LocalFileHandle = {
  getFile(): Promise<File>;
  createWritable(): Promise<WritableFile>;
};

type FilePickerWindow = Window & {
  showOpenFilePicker?: (options?: {
    multiple?: boolean;
    types?: Array<{
      description: string;
      accept: Record<string, string[]>;
    }>;
  }) => Promise<LocalFileHandle[]>;
};

const preferenceOptions: Array<{ value: ReviewChoice; label: string }> = [
  { value: 'a', label: 'Response A' },
  { value: 'b', label: 'Response B' },
  { value: 'tie', label: 'Tie' },
];

function parsePacket(text: string): ReviewRow[] {
  const rows = text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line, index) => {
      let candidate: unknown;
      try {
        candidate = JSON.parse(line);
      } catch {
        throw new Error(`Line ${index + 1} is not valid JSON.`);
      }

      if (!candidate || typeof candidate !== 'object') {
        throw new Error(`Line ${index + 1} is not a review case.`);
      }

      const row = candidate as Record<string, unknown>;
      for (const field of ['id', 'lineage_id', 'input_method', 'input', 'response_a', 'response_b']) {
        if (typeof row[field] !== 'string') {
          throw new Error(`Line ${index + 1} is missing the string field “${field}”.`);
        }
      }
      return candidate as ReviewRow;
    });

  if (!rows.length) {
    throw new Error('This packet is empty. Choose a review-checkpoint-*.jsonl file.');
  }
  return rows;
}

async function fingerprint(text: string): Promise<string> {
  const bytes = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return Array.from(new Uint8Array(digest))
    .slice(0, 12)
    .map((byte) => byte.toString(16).padStart(2, '0'))
    .join('');
}

function friendlyTitle(id: string): string {
  return id
    .replace(/^eval[-_]?/i, '')
    .replace(/[-_]+/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function claimsAreConsistent(pass: boolean | null | undefined, claims: string[] | undefined): boolean {
  if (pass === true) return !claims?.length;
  if (pass === false) return Boolean(claims?.some((claim) => claim.trim()));
  return false;
}

function isRowComplete(row: ReviewRow): boolean {
  return (
    isSideComplete(row, 'a') &&
    isSideComplete(row, 'b') &&
    Boolean(row.voice_preference) &&
    Boolean(row.overall_preference)
  );
}

function isSideComplete(row: ReviewRow, side: 'a' | 'b'): boolean {
  const factuality = side === 'a' ? row.factuality_a_pass : row.factuality_b_pass;
  const claims = side === 'a' ? row.unsupported_claims_a : row.unsupported_claims_b;
  const instruction =
    side === 'a' ? row.instruction_following_a_pass : row.instruction_following_b_pass;
  const burden = side === 'a' ? row.edit_burden_a : row.edit_burden_b;
  return (
    claimsAreConsistent(factuality, claims) &&
    typeof instruction === 'boolean' &&
    typeof burden === 'number'
  );
}

function packetJsonl(rows: ReviewRow[]): string {
  return `${rows.map((row) => JSON.stringify(row)).join('\n')}\n`;
}

function BooleanChoice({
  label,
  value,
  onChange,
}: {
  label: string;
  value: boolean | null | undefined;
  onChange: (value: boolean) => void;
}) {
  return (
    <fieldset>
      <legend className="mb-2 text-sm font-semibold text-stone-800">{label}</legend>
      <div className="grid grid-cols-2 gap-2">
        {[
          { label: 'Pass', value: true },
          { label: 'Fail', value: false },
        ].map((option) => (
          <button
            className={`rounded-lg border px-3 py-2 text-sm font-medium transition ${
              value === option.value
                ? option.value
                  ? 'border-emerald-700 bg-emerald-50 text-emerald-900'
                  : 'border-rose-700 bg-rose-50 text-rose-900'
                : 'border-stone-300 bg-white text-stone-600 hover:border-stone-500'
            }`}
            type="button"
            aria-pressed={value === option.value}
            key={option.label}
            onClick={() => onChange(option.value)}
          >
            {option.label}
          </button>
        ))}
      </div>
    </fieldset>
  );
}

function EditBurden({
  value,
  onChange,
}: {
  value: number | null | undefined;
  onChange: (value: number) => void;
}) {
  return (
    <fieldset>
      <div className="mb-2 flex items-baseline justify-between gap-3">
        <legend className="text-sm font-semibold text-stone-800">Edit burden</legend>
        <span className="text-xs text-stone-500">1 = publishable · 5 = rewrite</span>
      </div>
      <div className="grid grid-cols-5 gap-1.5">
        {[1, 2, 3, 4, 5].map((score) => (
          <button
            className={`rounded-lg border py-2 text-sm font-semibold transition ${
              value === score
                ? 'border-amber-700 bg-amber-50 text-amber-950'
                : 'border-stone-300 bg-white text-stone-600 hover:border-stone-500'
            }`}
            type="button"
            aria-label={`Edit burden ${score} out of 5`}
            aria-pressed={value === score}
            key={score}
            onClick={() => onChange(score)}
          >
            {score}
          </button>
        ))}
      </div>
    </fieldset>
  );
}

function PreferenceChoice({
  label,
  value,
  onChange,
}: {
  label: string;
  value: ReviewChoice | null | undefined;
  onChange: (value: ReviewChoice) => void;
}) {
  return (
    <fieldset>
      <legend className="mb-2 text-sm font-semibold text-stone-800">{label}</legend>
      <div className="grid grid-cols-3 gap-2">
        {preferenceOptions.map((option) => (
          <button
            className={`rounded-lg border px-3 py-2 text-sm font-medium transition ${
              value === option.value
                ? 'border-sky-700 bg-sky-50 text-sky-950'
                : 'border-stone-300 bg-white text-stone-600 hover:border-stone-500'
            }`}
            type="button"
            aria-pressed={value === option.value}
            key={option.value}
            onClick={() => onChange(option.value)}
          >
            {option.label}
          </button>
        ))}
      </div>
    </fieldset>
  );
}

function ResponseCard({
  side,
  row,
  onPatch,
}: {
  side: 'a' | 'b';
  row: ReviewRow;
  onPatch: (patch: Partial<ReviewRow>) => void;
}) {
  const upper = side.toUpperCase();
  const factualityKey = `factuality_${side}_pass` as const;
  const claimsKey = `unsupported_claims_${side}` as const;
  const instructionKey = `instruction_following_${side}_pass` as const;
  const burdenKey = `edit_burden_${side}` as const;
  const response = side === 'a' ? row.response_a : row.response_b;
  const factuality = row[factualityKey];
  const claims = row[claimsKey] ?? [];

  return (
    <article className="overflow-hidden rounded-2xl border border-stone-300 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-stone-200 px-5 py-4">
        <h2 className="font-mono text-sm font-bold uppercase tracking-[0.18em] text-stone-900">
          Response {upper}
        </h2>
        <span className="rounded-full bg-stone-100 px-2.5 py-1 text-xs text-stone-500">Blind</span>
      </div>
      <div className="review-scroll max-h-[58vh] min-h-80 overflow-y-auto border-b border-stone-200 px-5 py-5 sm:px-7 sm:py-7 lg:min-h-[32rem]">
        <div className="review-prose">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{response}</ReactMarkdown>
        </div>
      </div>
      <div className="space-y-5 bg-stone-50/70 p-5">
        <BooleanChoice
          label="Factuality"
          value={factuality}
          onChange={(value) =>
            onPatch({
              [factualityKey]: value,
              ...(value ? { [claimsKey]: [] } : {}),
            })
          }
        />
        {factuality === false && (
          <label className="block text-sm font-semibold text-stone-800">
            Unsupported claims
            <span className="mt-1 block text-xs font-normal text-stone-500">One specific claim per line.</span>
            <textarea
              className="mt-2 min-h-24 w-full resize-y rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm font-normal leading-6 outline-none transition focus:border-stone-700 focus:ring-2 focus:ring-stone-200"
              value={claims.join('\n')}
              onChange={(event) =>
                onPatch({
                  [claimsKey]: event.target.value
                    .split('\n')
                    .map((claim) => claim.trim())
                    .filter(Boolean),
                })
              }
              placeholder="State the unsupported claim…"
            />
          </label>
        )}
        <BooleanChoice
          label="Instruction following"
          value={row[instructionKey]}
          onChange={(value) => onPatch({ [instructionKey]: value })}
        />
        <EditBurden value={row[burdenKey]} onChange={(value) => onPatch({ [burdenKey]: value })} />
      </div>
    </article>
  );
}

export default function Home() {
  const [rows, setRows] = useState<ReviewRow[]>([]);
  const [fileName, setFileName] = useState('');
  const [storageKey, setStorageKey] = useState('');
  const [fileHandle, setFileHandle] = useState<LocalFileHandle | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [reviewStage, setReviewStage] = useState<ReviewStage>(0);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const current = rows[currentIndex];
  const completedCount = useMemo(() => rows.filter(isRowComplete).length, [rows]);
  const currentComplete = current ? isRowComplete(current) : false;

  useEffect(() => {
    if (rows.length && storageKey) {
      localStorage.setItem(storageKey, JSON.stringify(rows));
    }
  }, [rows, storageKey]);

  async function loadPacket(file: File, handle: LocalFileHandle | null = null) {
    setError('');
    setNotice('');
    try {
      const text = await file.text();
      const parsed = parsePacket(text);
      const key = `goodprose-review:${await fingerprint(text)}`;
      const cached = localStorage.getItem(key);
      let restored = parsed;

      if (cached) {
        try {
          const candidate = JSON.parse(cached) as ReviewRow[];
          const sameCases =
            Array.isArray(candidate) &&
            candidate.length === parsed.length &&
            candidate.every((row, index) => row.id === parsed[index].id);
          if (sameCases) restored = candidate;
        } catch {
          localStorage.removeItem(key);
        }
      }

      setRows(restored);
      setFileName(file.name);
      setStorageKey(key);
      setFileHandle(handle);
      const firstIncomplete = restored.findIndex((row) => !isRowComplete(row));
      setCurrentIndex(firstIncomplete === -1 ? 0 : firstIncomplete);
      setReviewStage(0);
      setNotice(cached ? 'Restored your browser-saved progress.' : 'Packet loaded. Progress now autosaves in this browser.');
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Could not open that packet.');
    }
  }

  async function openPacket() {
    const pickerWindow = window as FilePickerWindow;
    if (pickerWindow.showOpenFilePicker) {
      try {
        const [handle] = await pickerWindow.showOpenFilePicker.call(window, {
          multiple: false,
          types: [
            {
              description: 'JSON Lines review packet',
              accept: { 'application/json': ['.jsonl'] },
            },
          ],
        });
        if (handle) await loadPacket(await handle.getFile(), handle);
        return;
      } catch (caught) {
        if (caught instanceof DOMException && caught.name === 'AbortError') return;
      }
    }
    fileInputRef.current?.click();
  }

  function patchCurrent(patch: Partial<ReviewRow>) {
    setRows((existing) =>
      existing.map((row, index) => (index === currentIndex ? { ...row, ...patch } : row)),
    );
    setNotice('Draft autosaved locally.');
  }

  function goToCase(index: number, stage: ReviewStage = 0) {
    setCurrentIndex(index);
    setReviewStage(stage);
    setNotice('');
  }

  function stageIsComplete(stage: ReviewStage): boolean {
    if (!current) return false;
    if (stage === 0) return true;
    if (stage === 1) return isSideComplete(current, 'a');
    if (stage === 2) return isSideComplete(current, 'b');
    return currentComplete;
  }

  function previousStep() {
    if (reviewStage > 0) {
      setReviewStage((reviewStage - 1) as ReviewStage);
      setNotice('');
    } else if (currentIndex > 0) {
      goToCase(currentIndex - 1, 3);
    }
  }

  async function savePacket(forceDownload = false) {
    const output = packetJsonl(rows);
    if (fileHandle && !forceDownload) {
      try {
        const writable = await fileHandle.createWritable();
        await writable.write(output);
        await writable.close();
        setNotice(`Saved directly to ${fileName}.`);
        return;
      } catch {
        setNotice('Direct save was unavailable, so a completed copy was downloaded instead.');
      }
    }

    const blob = new Blob([output], { type: 'application/x-ndjson;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    const baseName = fileName.replace(/\.jsonl$/i, '') || 'review-packet';
    link.href = url;
    link.download = `${baseName}-completed.jsonl`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    setNotice(`Downloaded ${baseName}-completed.jsonl.`);
  }

  async function nextStep() {
    if (!stageIsComplete(reviewStage)) {
      setNotice('Complete the required choices on this step before continuing.');
      return;
    }
    if (reviewStage < 3) {
      setReviewStage((reviewStage + 1) as ReviewStage);
      setNotice('');
    } else if (currentIndex < rows.length - 1) {
      goToCase(currentIndex + 1, 0);
    } else {
      await savePacket();
    }
  }

  const hiddenInput = (
    <input
      ref={fileInputRef}
      className="sr-only"
      type="file"
      accept=".jsonl,application/json,application/x-ndjson"
      onChange={(event) => {
        const file = event.target.files?.[0];
        if (file) void loadPacket(file);
        event.target.value = '';
      }}
    />
  );

  if (!current) {
    return (
      <main className="min-h-screen px-5 py-8 sm:px-8 sm:py-12">
        {hiddenInput}
        <div className="mx-auto flex min-h-[calc(100vh-6rem)] max-w-5xl flex-col">
          <header className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="grid size-10 place-items-center rounded-xl bg-stone-900 font-serif text-lg font-bold text-white">G</div>
              <span className="text-sm font-semibold tracking-tight">GoodProse</span>
            </div>
            <span className="rounded-full border border-emerald-300 bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-900">
              Browser-local
            </span>
          </header>

          <section className="my-auto grid items-center gap-12 py-16 lg:grid-cols-[1.15fr_0.85fr]">
            <div>
              <p className="mb-4 font-mono text-xs font-bold uppercase tracking-[0.22em] text-amber-800">Blind checkpoint review</p>
              <h1 className="max-w-3xl font-serif text-5xl font-semibold leading-[1.03] tracking-[-0.035em] text-stone-950 sm:text-6xl">
                Review the writing, not the JSON.
              </h1>
              <p className="mt-6 max-w-2xl text-lg leading-8 text-stone-600">
                Open a checkpoint packet and score one blind A/B comparison at a time. Markdown is rendered cleanly, progress autosaves, and the exported JSONL works with the existing evaluator.
              </p>
              <div className="mt-8 flex flex-wrap items-center gap-4">
                <button
                  className="rounded-xl bg-stone-900 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-stone-700 focus:outline-none focus:ring-4 focus:ring-stone-300"
                  type="button"
                  onClick={() => void openPacket()}
                >
                  Open review packet
                </button>
                <span className="text-sm text-stone-500">Choose review-checkpoint-*.jsonl</span>
              </div>
              {error && <p className="mt-4 rounded-lg bg-rose-50 px-4 py-3 text-sm text-rose-800">{error}</p>}
            </div>

            <aside className="rounded-3xl border border-stone-300 bg-white p-7 shadow-[0_18px_55px_rgba(41,37,36,0.08)]">
              <p className="text-sm font-semibold text-stone-900">Your review stays private</p>
              <p className="mt-2 text-sm leading-6 text-stone-600">
                Packet contents are read and saved in your browser. This interface does not upload them to a server.
              </p>
              <ol className="mt-6 space-y-4 text-sm text-stone-700">
                {[
                  'Open one JSONL review packet.',
                  'Read the source, compare A and B, then score both.',
                  'Save the completed packet and run the existing summary command.',
                ].map((step, index) => (
                  <li className="flex gap-3" key={step}>
                    <span className="grid size-6 shrink-0 place-items-center rounded-full bg-amber-100 font-mono text-xs font-bold text-amber-900">{index + 1}</span>
                    <span className="pt-0.5">{step}</span>
                  </li>
                ))}
              </ol>
            </aside>
          </section>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#f7f4ed]">
      {hiddenInput}
      <header className="sticky top-0 z-30 border-b border-stone-300/80 bg-[#f7f4ed]/95 px-4 py-3 backdrop-blur sm:px-6">
        <div className="mx-auto flex max-w-[1600px] flex-wrap items-center justify-between gap-3">
          <div className="flex min-w-0 items-center gap-3">
            <div className="grid size-9 shrink-0 place-items-center rounded-lg bg-stone-900 font-serif font-bold text-white">G</div>
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-stone-950">GoodProse Blind Review</p>
              <p className="truncate font-mono text-[11px] text-stone-500">{fileName}</p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="hidden rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-900 sm:inline">Private · browser-local</span>
            <button className="rounded-lg border border-stone-300 bg-white px-3 py-2 text-xs font-semibold text-stone-700 hover:border-stone-500" type="button" onClick={() => void openPacket()}>
              Change packet
            </button>
            {fileHandle && (
              <button className="rounded-lg border border-stone-300 bg-white px-3 py-2 text-xs font-semibold text-stone-700 hover:border-stone-500" type="button" onClick={() => void savePacket(true)}>
                Download backup
              </button>
            )}
            <button className="rounded-lg bg-stone-900 px-3 py-2 text-xs font-semibold text-white hover:bg-stone-700" type="button" onClick={() => void savePacket()}>
              {fileHandle ? 'Save packet' : 'Export JSONL'}
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-[1600px] gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[220px_minmax(0,1fr)]">
        <aside className="self-start rounded-2xl border border-stone-300 bg-white p-4 lg:sticky lg:top-24">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-stone-900">Packet progress</p>
            <span className="font-mono text-xs text-stone-500">{completedCount}/{rows.length}</span>
          </div>
          <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-stone-200">
            <div className="h-full rounded-full bg-emerald-700 transition-all" style={{ width: `${(completedCount / rows.length) * 100}%` }} />
          </div>
          <nav className="mt-5 grid grid-cols-2 gap-2 lg:grid-cols-1" aria-label="Review cases">
            {rows.map((row, index) => {
              const complete = isRowComplete(row);
              const active = index === currentIndex;
              return (
                <button
                  className={`flex min-w-0 items-center gap-2 rounded-lg border px-3 py-2.5 text-left text-sm transition ${
                    active ? 'border-stone-900 bg-stone-900 text-white' : 'border-transparent text-stone-600 hover:border-stone-300 hover:bg-stone-50'
                  }`}
                  type="button"
                  key={row.id}
                  aria-current={active ? 'step' : undefined}
                  onClick={() => goToCase(index)}
                >
                  <span className={`grid size-5 shrink-0 place-items-center rounded-full text-[11px] font-bold ${complete ? 'bg-emerald-100 text-emerald-800' : active ? 'bg-white/15 text-white' : 'bg-stone-100 text-stone-500'}`}>
                    {complete ? '✓' : index + 1}
                  </span>
                  <span className="truncate">Case {index + 1}</span>
                </button>
              );
            })}
          </nav>
          <p className="mt-5 border-t border-stone-200 pt-4 text-xs leading-5 text-stone-500">
            A/B identities stay hidden until you run the summary with the matching key.
          </p>
        </aside>

        <div className="min-w-0 pb-24">
          <div className="mb-5">
            <p className="font-mono text-[11px] font-bold uppercase tracking-[0.16em] text-amber-800">
              Case {currentIndex + 1} of {rows.length} · {current.input_method.replaceAll('_', ' ')}
            </p>
            <h1 className="mt-1 font-serif text-2xl font-semibold tracking-tight text-stone-950 sm:text-3xl">
              {friendlyTitle(current.id)}
            </h1>
            <p className="mt-2 text-sm leading-6 text-stone-600">
              One task, two anonymous answers. Work left to right; only one long document appears at a time.
            </p>
          </div>

          <nav className="mb-5 grid grid-cols-2 gap-2 rounded-2xl border border-stone-300 bg-white p-2 sm:grid-cols-4" aria-label="Steps in this case">
            {[
              { label: '1. Request', complete: true },
              { label: '2. Response A', complete: isSideComplete(current, 'a') },
              { label: '3. Response B', complete: isSideComplete(current, 'b') },
              { label: '4. Final choice', complete: currentComplete },
            ].map((stage, index) => (
              <button
                className={`flex items-center justify-center gap-2 rounded-xl px-3 py-2.5 text-sm font-semibold transition ${
                  reviewStage === index
                    ? 'bg-stone-900 text-white'
                    : 'text-stone-600 hover:bg-stone-100'
                }`}
                type="button"
                key={stage.label}
                aria-current={reviewStage === index ? 'step' : undefined}
                onClick={() => setReviewStage(index as ReviewStage)}
              >
                {stage.complete && index > 0 && <span className="text-emerald-500">✓</span>}
                {stage.label}
              </button>
            ))}
          </nav>

          {reviewStage === 0 && (
            <section className="overflow-hidden rounded-2xl border border-amber-300 bg-white shadow-sm">
              <div className="border-b border-amber-200 bg-amber-50 px-5 py-5 sm:px-7">
                <span className="rounded-full bg-amber-200/70 px-2.5 py-1 text-xs font-bold text-amber-950">Context only · do not score this</span>
                <h2 className="mt-4 font-serif text-3xl font-semibold tracking-tight text-stone-950">What were both models asked to write?</h2>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-stone-700">
                  This is the original prompt, rough draft, or set of notes given to both models. It is not a third answer. Skim it for the requested facts, argument, and format so you can tell whether Responses A and B followed the assignment.
                </p>
              </div>
              <div className="review-scroll max-h-[55vh] overflow-y-auto px-5 py-6 sm:px-7">
                <div className="review-prose max-w-4xl">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{current.input}</ReactMarkdown>
                </div>
              </div>
            </section>
          )}

          {reviewStage === 1 && (
            <div className="mx-auto max-w-4xl">
              <div className="mb-4 rounded-xl border border-sky-200 bg-sky-50 px-4 py-3 text-sm leading-6 text-sky-950">
                Read Response A, then answer three things below it: Is it factual? Did it follow the request? How much editing would it need?
              </div>
              <ResponseCard side="a" row={current} onPatch={patchCurrent} />
            </div>
          )}

          {reviewStage === 2 && (
            <div className="mx-auto max-w-4xl">
              <div className="mb-4 rounded-xl border border-sky-200 bg-sky-50 px-4 py-3 text-sm leading-6 text-sky-950">
                Now review Response B using the same standards. The model identities remain hidden.
              </div>
              <ResponseCard side="b" row={current} onPatch={patchCurrent} />
            </div>
          )}

          {reviewStage === 3 && (
            <section className="mx-auto max-w-4xl rounded-2xl border border-stone-300 bg-white p-5 shadow-sm sm:p-7">
              <div className="mb-6">
                <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-bold text-emerald-900">Last step for this case</span>
                <h2 className="mt-4 font-serif text-3xl font-semibold tracking-tight text-stone-950">Which answer was better?</h2>
                <p className="mt-2 text-sm leading-6 text-stone-600">
                  You have already rated each answer. Make the direct comparison now; choose “Tie” when there is no meaningful winner.
                </p>
                <div className="mt-4 flex flex-wrap gap-2">
                  <button className="rounded-lg border border-stone-300 px-3 py-2 text-xs font-semibold text-stone-700 hover:bg-stone-50" type="button" onClick={() => setReviewStage(1)}>Review A again</button>
                  <button className="rounded-lg border border-stone-300 px-3 py-2 text-xs font-semibold text-stone-700 hover:bg-stone-50" type="button" onClick={() => setReviewStage(2)}>Review B again</button>
                </div>
              </div>
              <div className="grid gap-6 border-t border-stone-200 pt-6 lg:grid-cols-2">
                <PreferenceChoice label="Which sounds more like you?" value={current.voice_preference} onChange={(value) => patchCurrent({ voice_preference: value })} />
                <PreferenceChoice label="Which is better overall?" value={current.overall_preference} onChange={(value) => patchCurrent({ overall_preference: value })} />
              </div>
              <label className="mt-6 block text-sm font-semibold text-stone-800">
                What drove your choice? <span className="font-normal text-stone-500">(optional)</span>
                <textarea
                  className="mt-2 min-h-28 w-full resize-y rounded-xl border border-stone-300 bg-white px-3 py-3 text-sm font-normal leading-6 outline-none transition focus:border-stone-700 focus:ring-2 focus:ring-stone-200"
                  value={current.notes ?? ''}
                  onChange={(event) => patchCurrent({ notes: event.target.value || null })}
                  placeholder="For example: A had the stronger structure, but B sounded more natural…"
                />
              </label>
            </section>
          )}
        </div>
      </div>

      <footer className="fixed inset-x-0 bottom-0 z-30 border-t border-stone-300 bg-[#f7f4ed]/95 px-4 py-3 backdrop-blur sm:px-6">
        <div className="mx-auto flex max-w-[1600px] items-center justify-between gap-4 lg:pl-[244px]">
          <button
            className="rounded-lg border border-stone-300 bg-white px-4 py-2.5 text-sm font-semibold text-stone-700 disabled:cursor-not-allowed disabled:opacity-40"
            type="button"
            disabled={reviewStage === 0 && currentIndex === 0}
            onClick={previousStep}
          >
            Back
          </button>
          <p className={`hidden text-center text-xs sm:block ${stageIsComplete(reviewStage) ? 'text-emerald-800' : 'text-stone-500'}`} aria-live="polite">
            {notice || (stageIsComplete(reviewStage) ? 'This step is ready · draft autosaved' : 'Complete the choices on this step to continue')}
          </p>
          <button
            className="rounded-lg bg-stone-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-stone-700 disabled:cursor-not-allowed disabled:bg-stone-300"
            type="button"
            disabled={!stageIsComplete(reviewStage)}
            onClick={() => void nextStep()}
          >
            {reviewStage === 0 && 'Read Response A'}
            {reviewStage === 1 && 'Save A · Read B'}
            {reviewStage === 2 && 'Compare answers'}
            {reviewStage === 3 && (currentIndex === rows.length - 1 ? 'Finish & save packet' : 'Finish case · Next')}
          </button>
        </div>
      </footer>
    </main>
  );
}
