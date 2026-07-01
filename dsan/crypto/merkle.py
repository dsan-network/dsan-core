import hashlib

def hash_pair(a, b):
    return hashlib.sha256((a + b).encode()).hexdigest()

def merkle_root(hashes):

    if not hashes:
        return None

    level = hashes[:]

    while len(level) > 1:
        next_level = []

        for i in range(0, len(level), 2):
            left = level[i]

            if i + 1 < len(level):
                right = level[i + 1]
            else:
                right = left

            combined = hash_pair(left, right)
            next_level.append(combined)

        level = next_level

    return level[0]