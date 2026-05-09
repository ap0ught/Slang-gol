int wrap_coord(int value, int max_value)
{
    if (value < 0)
    {
        return max_value - 1;
    }

    if (value >= max_value)
    {
        return 0;
    }

    return value;
}

int count_neighbors(
    StructuredBuffer<uint> current,
    int x,
    int y,
    int width,
    int height
)
{
    int total = 0;

    for (int dy = -1; dy <= 1; dy++)
    {
        for (int dx = -1; dx <= 1; dx++)
        {
            if (dx == 0 && dy == 0)
            {
                continue;
            }

            int nx = wrap_coord(x + dx, width);
            int ny = wrap_coord(y + dy, height);
            int index = ny * width + nx;

            total += int(current[index]);
        }
    }

    return total;
}

void update_life_cell(
    StructuredBuffer<uint> current,
    RWStructuredBuffer<uint> next,
    int width,
    int height,
    int x,
    int y
)
{
    int index = y * width + x;

    uint alive = current[index];
    int neighbors = count_neighbors(current, x, y, width, height);

    uint result = 0;

    if (alive == 1 && (neighbors == 2 || neighbors == 3))
    {
        result = 1;
    }
    else if (alive == 0 && neighbors == 3)
    {
        result = 1;
    }

    next[index] = result;
}
