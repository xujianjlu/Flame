// Copyright 2010 . All Rights Reserved.
// Author: kingqj@gmail.com (Jing Qu)

#include "base/basictypes.h"
#include "base/fnv.h"
#include "base/logging.h"

namespace base {

void fnv128(const char* data, int len, void* digest) {
  if (data == NULL || digest == NULL || len < 0) {
    LOG(FATAL) << "Invalid parameter! fnv128 returned.";
    return;
  }

  // Initial hash value: 6C62272E 07BB0142 62B82175 6295C58D
  struct {
    uint64 word[2];
  } HashVal;

  HashVal.word[0] = 0x62B821756295C58DULL;
  HashVal.word[1] = 0x6C62272E07BB0142ULL;

  static const int kFNV_128_DIGEST_SIZE = 16;

  // If DataLen is zero, then hashing is not needed.
  if (len == 0) {
    memcpy(digest, HashVal.word, kFNV_128_DIGEST_SIZE);
    return;
  }

  uint64 val[4];

  val[0] = (HashVal.word[0] & 0x00000000ffffffffULL);
  val[1] = (HashVal.word[0] >> 32);
  val[2] = (HashVal.word[1] & 0x00000000ffffffffULL);
  val[3] = (HashVal.word[1] >> 32);

  // 128bit prime = 2^88 + 2^8 + 0x3b
  static const uint32 kFNV_128_PRIME_LOW = 0x13b;
  static const uint32 kFNV_128_PRIME_SHIFT = 24;

  int pos = 0;
  while (pos < len) {
    val[0] ^= (uint64) *data++;
    ++pos;

    // Multiplication
    uint64 tmp[4];

    tmp[0] = val[0] * kFNV_128_PRIME_LOW;
    tmp[1] = val[1] * kFNV_128_PRIME_LOW;
    tmp[2] = val[2] * kFNV_128_PRIME_LOW;
    tmp[3] = val[3] * kFNV_128_PRIME_LOW;

    tmp[2] += val[0] << kFNV_128_PRIME_SHIFT;
    tmp[3] += val[1] << kFNV_128_PRIME_SHIFT;

    // Propagate carries
    tmp[1] += (tmp[0] >> 32);
    val[0] = tmp[0] & 0x00000000ffffffffULL;

    tmp[2] += (tmp[1] >> 32);
    val[1] = tmp[1] & 0x00000000ffffffffULL;

    val[3] = tmp[3] + (tmp[2] >> 32);
    val[2] = tmp[2] & 0x00000000ffffffffULL;
  }

  HashVal.word[1] = ((val[3]<<32) | val[2]);
  HashVal.word[0] = ((val[1]<<32) | val[0]);

  memcpy(digest, HashVal.word, kFNV_128_DIGEST_SIZE);
}

}  // namespace base
