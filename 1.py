import random, time, threading, heapq, sys

def generate_data(n: int, seed: int = 42) -> list:
    rng = random.Random(seed)
    return [rng.randint(0, 100_000_000) for _ in range(n)]


def save_to_file(arr: list, filename: str) -> None:
    with open(filename, "w") as f:
        f.write(f"{len(arr)}\n")
        for x in arr:
            f.write(f"{x}\n")
    print(f"✅ Дані збережено у файл: {filename}")


def load_from_file(filename: str) -> list:
    try:
        with open(filename) as f:
            n = int(f.readline())
            return [int(f.readline()) for _ in range(n)]
    except FileNotFoundError:
        print("❌ Помилка: Файл не знайдено.")
        return None


def counting_sort_by_digit(arr: list, exp: int) -> list:
    n = len(arr)
    count = [0] * 10
    output = [0] * n
    for num in arr:
        count[(num // exp) % 10] += 1
    for i in range(1, 10):
        count[i] += count[i - 1]
    for i in range(n - 1, -1, -1):
        digit = (arr[i] // exp) % 10
        count[digit] -= 1
        output[count[digit]] = arr[i]
    return output


def radix_sort_sequential(arr: list) -> list:
    if not arr: return arr
    max_val = max(arr)
    exp = 1
    result = arr[:]
    while max_val // exp > 0:
        result = counting_sort_by_digit(result, exp)
        exp *= 10
    return result


def _sort_chunk(chunk: list, out: list, idx: int) -> None:
    out[idx] = radix_sort_sequential(chunk)


def k_way_merge(sorted_chunks: list) -> list:
    heap = []
    iters = [iter(c) for c in sorted_chunks]
    result = []
    for i, it in enumerate(iters):
        val = next(it, None)
        if val is not None:
            heapq.heappush(heap, (val, i))
    while heap:
        val, i = heapq.heappop(heap)
        result.append(val)
        nxt = next(iters[i], None)
        if nxt is not None:
            heapq.heappush(heap, (nxt, i))
    return result


def radix_sort_parallel(arr: list, num_threads: int = 4) -> list:
    if not arr: return arr
    chunk_size = (len(arr) + num_threads - 1) // num_threads
    chunks = [arr[i:i + chunk_size] for i in range(0, len(arr), chunk_size)]
    sorted_chunks = [None] * len(chunks)
    threads = [
        threading.Thread(target=_sort_chunk, args=(chunk, sorted_chunks, i))
        for i, chunk in enumerate(chunks)
    ]
    for t in threads: t.start()
    for t in threads: t.join()
    return k_way_merge(sorted_chunks)


# Консольне меню

def main_menu():
    arr = None
    threads_count = 4

    while True:
        print("\n--- RADIX SORT BENCHMARK---")
        print(f"Потоків для паралелізму: {threads_count}")
        print("1. Згенерувати новий масив")
        print("2. Зберегти поточний масив у файл")
        print("3. Завантажити масив з файлу")
        print("4. Запустити порівняння (Seq vs Parallel)")
        print("5. Змінити кількість потоків")
        print("6. Показати приклад на 10 елементах")
        print("0. Вихід")

        choice = input("\nОберіть дію: ")

        if choice == "1":
            n = int(input("Введіть розмір масиву (напр. 1000000): "))
            arr = generate_data(n)
            print(f"✨ Згенеровано {n} елементів.")

        elif choice == "2":
            if arr:
                name = input("Назва файлу (напр. data.txt): ")
                save_to_file(arr, name)
            else:
                print("⚠️ Спочатку згенеруйте або завантажте дані!")

        elif choice == "3":
            name = input("Назва файлу для зчитування: ")
            arr = load_from_file(name)
            if arr: print(f"✅ Завантажено {len(arr)} елементів.")

        elif choice == "4":
            if not arr:
                print("⚠️ Немає даних для сортування!")
                continue

            print(f"\nСортування {len(arr)} елементів...")

            # Послідовно
            t0 = time.perf_counter()
            r_seq = radix_sort_sequential(arr[:])
            t_seq = time.perf_counter() - t0
            print(f"⏱ Послідовно: {t_seq:.4f} сек")

            # Паралельно
            t0 = time.perf_counter()
            r_par = radix_sort_parallel(arr[:], threads_count)
            t_par = time.perf_counter() - t0
            print(f"🚀 Паралельно: {t_par:.4f} сек")

            print(f"📈 Прискорення: {t_seq / t_par:.2f}x")
            assert r_seq == r_par, "Помилка: результати не збігаються!"

        elif choice == "5":
            threads_count = int(input("Введіть кількість потоків: "))

        elif choice == "6":
            example = [random.randint(1, 1000) for _ in range(10)]
            print(f"\nВхідний масив:      {example}")
            sorted_seq = radix_sort_sequential(example[:])
            sorted_par = radix_sort_parallel(example[:], 4)
            print(f"Після сортування:   {sorted_seq}")
            assert sorted_seq == sorted_par
            print(f"✅ Відсортовано!")

        elif choice == "0":
            print("Бувай!")
            break
        else:
            print("❌ Невірний вибір.")


if __name__ == "__main__":
    main_menu()