from PIL import Image, ImageDraw
import random
import os

class Mondrian(object):
    def __init__(self):
        self.set_client_size(1920, 1200)

    def set_client_size(self, w, h):
        self.client_size = (w, h)
        self.reset()

    def reset(self):
        cw, ch = self.client_size
        self.size = self.find_divisor(self.client_size)
        self.bounds = (cw // self.size, ch // self.size)
        w, h = self.bounds
        self.bounds = (w + 2, h + 2)
        w, h = self.bounds
        self.grid = grid = [[0] * w for _ in range(h)]

        # walled perimeter
        for y in range(h):
            grid[y][0] = 1
            grid[y][w - 1] = 1
        for x in range(w):
            grid[0][x] = 2
            grid[h - 1][x] = 2

        # split
        split_count = random.randint(4, 16)
        _split_count = split_count
        splits = set([(1, 0), (1, w - 1), (2, 0), (2, h - 1)])
        while split_count:
            split = self.split(grid, splits)
            if split is not None:
                splits.add(split)
                split_count -= 1

        # locate all regions
        regions = []
        for y in range(h):
            for x in range(w):
                if grid[y][x] != 0:
                    continue
                regions.append((x, y))
                self.fill(grid, x, y, -1)

        random.shuffle(regions)

        # fill colors
        fill_count = random.randint(2, min(_split_count, 6))
        while fill_count:
            x, y = regions.pop()
            c = random.randint(3, 5)
            self.fill(grid, x, y, c)
            fill_count -= 1

        # fill white
        while regions:
            x, y = regions.pop()
            self.fill(grid, x, y, 0)

    def split(self, grid, splits):
        w, h = self.bounds
        p = 4
        d = random.randint(1, 2)

        if d == 1:
            x = random.randint(0, w - 1)
            for dx in range(-p, p + 1):
                if (1, x + dx) in splits:
                    return None

            p = []
            for y in range(0, h):
                if grid[y][x] == 2:
                    p.append(y)
                    
            if len(p) < 2:
                return None

            a, b = sorted(random.sample(p, 2))

            for y in range(a, b + 1):
                grid[y][x] = 1

            return (1, x)

        else:
            y = random.randint(0, h - 1)
            for dy in range(-p, p + 1):
                if (2, y + dy) in splits:
                    return None

            p = []
            for x in range(0, w):
                if grid[y][x] == 1:
                    p.append(x)

            if len(p) < 2:
                return None

            a, b = sorted(random.sample(p, 2))
            for x in range(a, b + 1):
                grid[y][x] = 2

            return (2, y)

    def fill(self, grid, x, y, c):
        color = grid[y][x]
        queue = set([(x, y)])

        while queue:
            x, y = queue.pop()

            if grid[y][x] != color:
                continue

            grid[y][x] = c

            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    queue.add((x + dx, y + dy))

    def render(self):
        img = Image.new('RGB', self.client_size, (255, 255, 255))
        draw = ImageDraw.Draw(img)

        colors = [
            (255, 255, 255),
            (0, 0, 0),
            (0, 0, 0),
            (204, 0, 11),
            (1, 102, 186),
            (249, 213, 26),
        ]

        n = self.size
        w, h = self.bounds

        for x in range(w - 2):
            for y in range(h - 2):
                i, j = x * n, y * n
                color = colors[self.grid[y + 1][x + 1]]
                draw.rectangle([(i, j), (i + n, j + n)], color)

        return img

    def find_divisor(self, dimensions, tolerance=5):
        w, h = dimensions
        greater_candidate = smaller_candidate = max(w, h) // 100
        diff = 1

        while diff <= tolerance:
            if w % smaller_candidate == 0 and h % smaller_candidate == 0:
                return smaller_candidate

            if w % greater_candidate == 0 and h % greater_candidate == 0:
                return greater_candidate

            greater_candidate += diff
            smaller_candidate -= diff
            diff += 1

        raise ValueError(('Could not find a common divisor of height ({1}px) and '
        'width ({2}px) within the tolerance of {0}px.').format(tolerance, *dimensions))


def main():
    mondrian = Mondrian()
    img = mondrian.render()

    wallpaper_folder = os.environ.get('WALLPAPER_FOLDER', '.')

    img.save(wallpaper_folder + '/wallpaper.jpg')

if __name__ == '__main__':
    main()
