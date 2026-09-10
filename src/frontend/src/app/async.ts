// Utilitas async terpusat.

// Jalankan `fn` untuk tiap item TAPI batasi berapa banyak yang berjalan
// bersamaan (concurrency). Dipakai untuk fan-out ke banyak endpoint (mis.
// fetch task per column / timer log per task untuk semua board) supaya tidak
// menembak backend dengan ratusan request serentak → kena rate limit 429.
// Urutan hasil tetap sama dengan urutan input.
export async function mapLimit<T, R>(
    items: readonly T[],
    limit: number,
    fn: (item: T, index: number) => Promise<R>,
): Promise<R[]> {
    const results = new Array<R>(items.length)
    let cursor = 0

    async function worker() {
        while (cursor < items.length) {
            const index = cursor++
            results[index] = await fn(items[index], index)
        }
    }

    const workers = Array.from(
        { length: Math.min(Math.max(1, limit), items.length) },
        () => worker(),
    )
    await Promise.all(workers)
    return results
}
