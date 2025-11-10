#pragma once

#include "dario.h"
#include "layers.h"

// Skeletyl is native 36-key (3x5_3)
// Wrapper macro to force expansion of LAYER_* macros before passing to LAYOUT
#define LAYOUT_wrapper(...) LAYOUT_split_3x5_3(__VA_ARGS__)
