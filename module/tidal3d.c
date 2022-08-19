#include <math.h>

#include "py/runtime.h"
#include "py/binary.h"

// Pre-computed PI over 180
#define DEGS_TO_RADS (0.017453)

// Internal helper to calculate vector magnitude used by v_magnitude and v_normalise
STATIC mp_float_t v_magnitude_internal(mp_obj_t *vec, size_t len) {
	mp_float_t sum = 0;
	for (size_t i = 0; i < len; i++) {
		mp_float_t f = mp_obj_get_float(vec[i]);
		sum += f * f;
	}
	return sqrt(sum);
}

/**
 * Returns the magnitude (length) of the given vector as a scalar value
 */
STATIC mp_obj_t v_magnitude(mp_obj_t vector) {
	size_t len;
	mp_obj_t *vec;
	mp_obj_get_array(vector, &len, &vec);

	return mp_obj_new_float(v_magnitude_internal(vec, len));
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(v_magnitude_obj, v_magnitude);

/**
 * Normalises the given vector to unit length
 */
STATIC mp_obj_t v_normalise(size_t n_args, const mp_obj_t *args) {
	mp_obj_t *vec, *dest;
	mp_obj_get_array_fixed_n(args[0], 3, &vec);
	if (n_args > 1) {
		mp_obj_get_array_fixed_n(args[1], 3, &dest);
	} else {
		dest = vec;
	}

	mp_float_t mag = v_magnitude_internal(vec, 3);

	for (size_t i = 0; i < 3; i++) {
		mp_float_t f = mp_obj_get_float(vec[i]);
		// Avoid divide by zero on zero-length vectors
		if (mag == 0) {
			dest[i] = mp_obj_new_float(f);
		} else {
			dest[i] = mp_obj_new_float(f / mag);
		}
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(v_normalise_obj, 1, 2, v_normalise);

/**
 * Scales the given vector by the given scalar factor
 */
STATIC mp_obj_t v_scale(size_t n_args, const mp_obj_t *args) {
	mp_obj_t *vec, *dest;
	mp_obj_get_array_fixed_n(args[0], 3, &vec);

	mp_float_t f = mp_obj_get_float(args[1]);

	if (n_args > 2) {
		mp_obj_get_array_fixed_n(args[2], 3, &dest);
	} else {
		dest = vec;
	}

	for (size_t i = 0; i < 3; i++) {
		dest[i] = mp_obj_new_float(mp_obj_get_float(vec[i]) * f);
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(v_scale_obj, 2, 3, v_scale);

/**
 * Adds the second given 3D vector to the first given 3D vector
 */
STATIC mp_obj_t v_add(size_t n_args, const mp_obj_t *args) {
	mp_obj_t *vec1, *vec2, *dest;
	mp_obj_get_array_fixed_n(args[0], 3, &vec1);
	mp_obj_get_array_fixed_n(args[1], 3, &vec2);
	if (n_args > 2) {
		mp_obj_get_array_fixed_n(args[2], 3, &dest);
	} else {
		dest = vec1;
	}

	for (size_t i = 0; i < 3; i++) {
		dest[i] = mp_obj_new_float(mp_obj_get_float(vec1[i]) + mp_obj_get_float(vec2[i]));
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(v_add_obj, 2, 3, v_add);

/**
 * Subtracts the second given 3D vector from the first given 3D vector
 */
STATIC mp_obj_t v_subtract(size_t n_args, const mp_obj_t *args) {
	mp_obj_t *vec1, *vec2, *dest;
	mp_obj_get_array_fixed_n(args[0], 3, &vec1);
	mp_obj_get_array_fixed_n(args[1], 3, &vec2);
	if (n_args > 2) {
		mp_obj_get_array_fixed_n(args[2], 3, &dest);
	} else {
		dest = vec1;
	}

	for (size_t i = 0; i < 3; i++) {
		dest[i] = mp_obj_new_float(mp_obj_get_float(vec1[i]) - mp_obj_get_float(vec2[i]));
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(v_subtract_obj, 2, 3, v_subtract);

/**
 * Averages the list of given vectors, although this can be expressed as a composition of v_add
 * and v_scale, it is much quicker done as a single call
 */
STATIC mp_obj_t v_average(size_t n_args, const mp_obj_t *args) {
	size_t list_len;
	mp_obj_t *list, *dest;
	mp_obj_get_array(args[0], &list_len, &list);
	mp_obj_get_array_fixed_n(args[1], 3, &dest);

	mp_float_t x = 0, y = 0, z = 0;

	mp_obj_t *vec;
	for (size_t i = 0; i < list_len; i++) {
		mp_obj_get_array_fixed_n(list[i], 3, &vec);
		x += mp_obj_get_float(vec[0]);
		y += mp_obj_get_float(vec[1]);
		z += mp_obj_get_float(vec[2]);
	}

	dest[0] = mp_obj_new_float(x / list_len);
	dest[1] = mp_obj_new_float(y / list_len);
	dest[2] = mp_obj_new_float(z / list_len);
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(v_average_obj, 2, 2, v_average);

/**
 * Multiplies the given 3D vector by the given 4x4 matrix
 */
STATIC mp_obj_t v_multiply(size_t n_args, const mp_obj_t *args) {
	mp_obj_t *vec, *dest;
	mp_obj_get_array_fixed_n(args[0], 3, &vec);

	mp_buffer_info_t mat_buffer;
	mp_get_buffer_raise(args[1], &mat_buffer, MP_BUFFER_READ);

	if (n_args > 2) {
		mp_obj_get_array_fixed_n(args[2], 3, &dest);
	} else {
		dest = vec;
	}

	mp_float_t x = mp_obj_get_float(vec[0]);
	mp_float_t y = mp_obj_get_float(vec[1]);
	mp_float_t z = mp_obj_get_float(vec[2]);

	mp_float_t xyzw[4];
	for (size_t i = 0; i < 4; i++) {
		xyzw[i] = x * ((float *)mat_buffer.buf)[i]
			+ y * ((float *)mat_buffer.buf)[4 + i]
			+ z * ((float *)mat_buffer.buf)[8 + i]
			+ ((float *)mat_buffer.buf)[12 + i];
	}

	dest[0] = mp_obj_new_float(xyzw[0] / xyzw[3]);
	dest[1] = mp_obj_new_float(xyzw[1] / xyzw[3]);
	dest[2] = mp_obj_new_float(xyzw[2] / xyzw[3]);
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(v_multiply_obj, 2, 3, v_multiply);

/**
 * Multiplies each of the 3D vectors in the given list by the given 4x4 matrix
 */
STATIC mp_obj_t v_multiply_batch(size_t n_args, const mp_obj_t *args) {
	size_t list_len;
	mp_obj_t *vec_list, *dest_list;
	mp_obj_get_array(args[0], &list_len, &vec_list);

	mp_buffer_info_t mat_buffer;
	mp_get_buffer_raise(args[1], &mat_buffer, MP_BUFFER_READ);

	if (n_args > 2) {
		mp_obj_get_array(args[2], &list_len, &dest_list);
	} else {
		dest_list = vec_list;
	}

	mp_obj_t *vec, *dest;
	mp_float_t x, y, z;
	mp_float_t xyzw[4];
	for (size_t j = 0; j < list_len; j++) {
		mp_obj_get_array_fixed_n(vec_list[j], 3, &vec);
		mp_obj_get_array_fixed_n(dest_list[j], 3, &dest);

		x = mp_obj_get_float(vec[0]);
		y = mp_obj_get_float(vec[1]);
		z = mp_obj_get_float(vec[2]);

		for (size_t i = 0; i < 4; i++) {
			xyzw[i] = x * ((float *)mat_buffer.buf)[i]
				+ y * ((float *)mat_buffer.buf)[4 + i]
				+ z * ((float *)mat_buffer.buf)[8 + i]
				+ ((float *)mat_buffer.buf)[12 + i];
		}
		dest[0] = mp_obj_new_float(xyzw[0] / xyzw[3]);
		dest[1] = mp_obj_new_float(xyzw[1] / xyzw[3]);
		dest[2] = mp_obj_new_float(xyzw[2] / xyzw[3]);
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(v_multiply_batch_obj, 2, 3, v_multiply_batch);

/**
 * Returns a scalar value of 0 if the given 3D vectors are exactly perpendicular, <0 if the angle
 * between them is greater than 90° or >0 if the angle between them is less than 90° (dot product)
 */
STATIC mp_obj_t v_dot(mp_obj_t vector1, mp_obj_t vector2) {
	mp_obj_t *v1, *v2;
	mp_obj_get_array_fixed_n(vector1, 3, &v1);
	mp_obj_get_array_fixed_n(vector2, 3, &v2);

	mp_float_t result;
	result = mp_obj_get_float(v1[0]) * mp_obj_get_float(v2[0]);
	result += mp_obj_get_float(v1[1]) * mp_obj_get_float(v2[1]);
	result += mp_obj_get_float(v1[2]) * mp_obj_get_float(v2[2]);
	return mp_obj_new_float(result);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(v_dot_obj, v_dot);

/**
 * Multiplies the given 3D vector by the second 3D vector to yield the vector that is exactly
 * perpendicular to both (cross product)
 */
STATIC mp_obj_t v_cross(size_t n_args, const mp_obj_t *args) {
	mp_obj_t *vec1, *vec2, *dest;
	mp_obj_get_array_fixed_n(args[0], 3, &vec1);
	mp_obj_get_array_fixed_n(args[1], 3, &vec2);
	if (n_args > 2) {
		mp_obj_get_array_fixed_n(args[2], 3, &dest);
	} else {
		dest = vec1;
	}

	mp_float_t xyz[3];
	for (size_t i = 0, n = 0, nn = 0; i < 3; i++) {
		n = (i + 1) % 3;
		nn = (i + 2) % 3;
		xyz[i] = mp_obj_get_float(vec1[n]) * mp_obj_get_float(vec2[nn]) -
			 mp_obj_get_float(vec1[nn]) * mp_obj_get_float(vec2[n]);
	}
	dest[0] = mp_obj_new_float(xyz[0]);
	dest[1] = mp_obj_new_float(xyz[1]);
	dest[2] = mp_obj_new_float(xyz[2]);
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(v_cross_obj, 2, 3, v_cross);

/**
 * Return screen coordinates for a list of vertices containing normalised device coordinates (NDCs),
 * an NDC with x and y values of between -1.0 and 1.0 are mapped to valid screen coordinates within
 * the contraints of the given screen dimensions in pixels
 *
 * vectors: Vertices for a single face as a list of lists
 * coords: A pre-allocated array of size (vertices * 2) where the screen coords will be written
 * width: Width of the screen in pixels
 * height: Height of the screen in pixels
 */
STATIC mp_obj_t v_ndc_to_screen(size_t n_args, const mp_obj_t *args) {
	size_t list_len;
	mp_obj_t *vecs, *vec;
	mp_obj_get_array(args[0], &list_len, &vecs);

	mp_buffer_info_t bufinfo;
	mp_get_buffer_raise(args[1], &bufinfo, MP_BUFFER_WRITE);

	mp_float_t w = mp_obj_get_float(args[2]);
	mp_float_t h = mp_obj_get_float(args[3]);

	for (size_t i = 0; i < list_len; i++) {
		mp_obj_get_array_fixed_n(vecs[i], 3, &vec);

		mp_int_t x = (mp_obj_get_float(vec[0]) + 1) * 0.5 * w;
		mp_int_t y = (1 - (mp_obj_get_float(vec[1]) + 1) * 0.5) * h;

		mp_binary_set_val_array_from_int(bufinfo.typecode, bufinfo.buf, i * 2, x);
		mp_binary_set_val_array_from_int(bufinfo.typecode, bufinfo.buf, i * 2 + 1, y);
	}

	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(v_ndc_to_screen_obj, 4, 4, v_ndc_to_screen);

// Internal helper to calculate matrix multiplication used by m_multiply, m_translate and m_rotate
STATIC void m_multiply_internal(mp_buffer_info_t *dest, float *mat1, float *mat2) {
	float m0[4], m1[4], m2[4], m3[4];

	m0[0] = mat1[0] * mat2[0] + mat1[1] * mat2[4] + mat1[2] * mat2[8] + mat1[3] * mat2[12];
	m0[1] = mat1[0] * mat2[1] + mat1[1] * mat2[5] + mat1[2] * mat2[9] + mat1[3] * mat2[13];
	m0[2] = mat1[0] * mat2[2] + mat1[1] * mat2[6] + mat1[2] * mat2[10] + mat1[3] * mat2[14];
	m0[3] = mat1[0] * mat2[3] + mat1[1] * mat2[7] + mat1[2] * mat2[11] + mat1[3] * mat2[15];

	m1[0] = mat1[4] * mat2[0] + mat1[5] * mat2[4] + mat1[6] * mat2[8] + mat1[7] * mat2[12];
	m1[1] = mat1[4] * mat2[1] + mat1[5] * mat2[5] + mat1[6] * mat2[9] + mat1[7] * mat2[13];
	m1[2] = mat1[4] * mat2[2] + mat1[5] * mat2[6] + mat1[6] * mat2[10] + mat1[7] * mat2[14];
	m1[3] = mat1[4] * mat2[3] + mat1[5] * mat2[7] + mat1[6] * mat2[11] + mat1[7] * mat2[15];

	m2[0] = mat1[8] * mat2[0] + mat1[9] * mat2[4] + mat1[10] * mat2[8] + mat1[11] * mat2[12];
	m2[1] = mat1[8] * mat2[1] + mat1[9] * mat2[5] + mat1[10] * mat2[9] + mat1[11] * mat2[13];
	m2[2] = mat1[8] * mat2[2] + mat1[9] * mat2[6] + mat1[10] * mat2[10] + mat1[11] * mat2[14];
	m2[3] = mat1[8] * mat2[3] + mat1[9] * mat2[7] + mat1[10] * mat2[11] + mat1[11] * mat2[15];

	m3[0] = mat1[12] * mat2[0] + mat1[13] * mat2[4] + mat1[14] * mat2[8] + mat1[15] * mat2[12];
	m3[1] = mat1[12] * mat2[1] + mat1[13] * mat2[5] + mat1[14] * mat2[9] + mat1[15] * mat2[13];
	m3[2] = mat1[12] * mat2[2] + mat1[13] * mat2[6] + mat1[14] * mat2[10] + mat1[15] * mat2[14];
	m3[3] = mat1[12] * mat2[3] + mat1[13] * mat2[7] + mat1[14] * mat2[11] + mat1[15] * mat2[15];

	for (size_t i = 0; i < 4; i++) {
		mp_binary_set_val_array(dest->typecode, dest->buf, i, mp_obj_new_float(m0[i]));
		mp_binary_set_val_array(dest->typecode, dest->buf, i + 4, mp_obj_new_float(m1[i]));
		mp_binary_set_val_array(dest->typecode, dest->buf, i + 8, mp_obj_new_float(m2[i]));
		mp_binary_set_val_array(dest->typecode, dest->buf, i + 12, mp_obj_new_float(m3[i]));
	}
}

/**
 * Multiplies the given 4x4 matrix by the second given 4x4 matrix
 */
STATIC mp_obj_t m_multiply(mp_obj_t matrix1, mp_obj_t matrix2) {
	mp_buffer_info_t mat1_buffer, mat2_buffer;
	mp_get_buffer_raise(matrix1, &mat1_buffer, MP_BUFFER_RW);
	mp_get_buffer_raise(matrix2, &mat2_buffer, MP_BUFFER_READ);

	// Perform the multiplication
	m_multiply_internal(&mat1_buffer, ((float *)mat1_buffer.buf), ((float *)mat2_buffer.buf));
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(m_multiply_obj, m_multiply);

/**
 * Translates the given 4x4 matrix by the given 3D vector
 */
STATIC mp_obj_t m_translate(mp_obj_t matrix, mp_obj_t vector) {
	mp_buffer_info_t mat_buffer;
	mp_get_buffer_raise(matrix, &mat_buffer, MP_BUFFER_RW);

	// Generate the translation matrix
	mp_obj_t *vec;
	mp_obj_get_array_fixed_n(vector, 3, &vec);
	float trans_mat[16] = {
		1, 0, 0, 0,
		0, 1, 0, 0,
		0, 0, 1, 0,
		0, 0, 0, 1
	};
	trans_mat[12] = mp_obj_get_float(vec[0]);
	trans_mat[13] = mp_obj_get_float(vec[1]);
	trans_mat[14] = mp_obj_get_float(vec[2]);

	// Perform the multiplication
	m_multiply_internal(&mat_buffer, ((float *)mat_buffer.buf), trans_mat);
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(m_translate_obj, m_translate);

/**
 * Rotates the given 4x4 matrix by the given quaternion
 */
STATIC mp_obj_t m_rotate(mp_obj_t matrix, mp_obj_t quaternion) {
	mp_buffer_info_t mat_buffer, quat_buffer;
	mp_get_buffer_raise(matrix, &mat_buffer, MP_BUFFER_RW);
	mp_get_buffer_raise(quaternion, &quat_buffer, MP_BUFFER_READ);

	// Generate the rotation matrix
	float w = ((float *)quat_buffer.buf)[0];
	float x = ((float *)quat_buffer.buf)[1];
	float y = ((float *)quat_buffer.buf)[2];
	float z = ((float *)quat_buffer.buf)[3];
	float rot_mat[16] = {
		1, 0, 0, 0,
		0, 1, 0, 0,
		0, 0, 1, 0,
		0, 0, 0, 1
	};
	rot_mat[0] = 1 - 2 * (y * y + z * z);
	rot_mat[1] = 2 * (x * y - w * z);
	rot_mat[2] = 2 * (x * z + w * y);
	rot_mat[4] = 2 * (x * y + w * z);
	rot_mat[5] = 1 - 2 * (x * x + z * z);
	rot_mat[6] = 2 * (y * z - w * x);
	rot_mat[8] = 2 * (x * z - w * y);
	rot_mat[9] = 2 * (y * z + w * x);
	rot_mat[10] = 1 - 2 * (x * x + y * y);

	// Perform the multiplication
	m_multiply_internal(&mat_buffer, ((float *)mat_buffer.buf), rot_mat);
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(m_rotate_obj, m_rotate);

/**
 * Rotates the given quaternion by the given number of degrees around the axis described by the
 * given 3D vector
 */
STATIC mp_obj_t q_rotate(mp_obj_t quaternion, mp_obj_t degrees, mp_obj_t vector) {
	mp_buffer_info_t quat_buffer;
	mp_get_buffer_raise(quaternion, &quat_buffer, MP_BUFFER_RW);

	mp_obj_t *vec;
	mp_obj_get_array_fixed_n(vector, 3, &vec);

	float q1w = ((float *)quat_buffer.buf)[0];
	float q1x = ((float *)quat_buffer.buf)[1];
	float q1y = ((float *)quat_buffer.buf)[2];
	float q1z = ((float *)quat_buffer.buf)[3];

	// Compute a rotation quaternion from the angle and vector
	float theta = (mp_obj_get_float(degrees) * DEGS_TO_RADS) / 2;
	float factor = sin(theta);
	float q2w = cos(theta);
	float q2x = mp_obj_get_float(vec[0]) * factor;
	float q2y = mp_obj_get_float(vec[1]) * factor;
	float q2z = mp_obj_get_float(vec[2]) * factor;

	// Multiply the given quaternion by the rotation quaternion
	mp_binary_set_val_array(quat_buffer.typecode, quat_buffer.buf, 0, mp_obj_new_float(q1w * q2w - q1x * q2x - q1y * q2y - q1z * q2z));
	mp_binary_set_val_array(quat_buffer.typecode, quat_buffer.buf, 1, mp_obj_new_float(q1w * q2x + q1x * q2w + q1y * q2z - q1z * q2y));
	mp_binary_set_val_array(quat_buffer.typecode, quat_buffer.buf, 2, mp_obj_new_float(q1w * q2y - q1x * q2z + q1y * q2w + q1z * q2x));
	mp_binary_set_val_array(quat_buffer.typecode, quat_buffer.buf, 3, mp_obj_new_float(q1w * q2z + q1x * q2y - q1y * q2x + q1z * q2w));
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_3(q_rotate_obj, q_rotate);

#if !MICROPY_ENABLE_DYNRUNTIME
STATIC const mp_rom_map_elem_t tidal3d_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_tidal3d) },
    { MP_ROM_QSTR(MP_QSTR_v_magnitude), MP_ROM_PTR(&v_magnitude_obj) },
    { MP_ROM_QSTR(MP_QSTR_v_normalise), MP_ROM_PTR(&v_normalise_obj) },
    { MP_ROM_QSTR(MP_QSTR_v_scale), MP_ROM_PTR(&v_scale_obj) },
    { MP_ROM_QSTR(MP_QSTR_v_add), MP_ROM_PTR(&v_add_obj) },
    { MP_ROM_QSTR(MP_QSTR_v_subtract), MP_ROM_PTR(&v_subtract_obj) },
    { MP_ROM_QSTR(MP_QSTR_v_average), MP_ROM_PTR(&v_average_obj) },
    { MP_ROM_QSTR(MP_QSTR_v_multiply), MP_ROM_PTR(&v_multiply_obj) },
    { MP_ROM_QSTR(MP_QSTR_v_multiply_batch), MP_ROM_PTR(&v_multiply_batch_obj) },
    { MP_ROM_QSTR(MP_QSTR_v_dot), MP_ROM_PTR(&v_dot_obj) },
    { MP_ROM_QSTR(MP_QSTR_v_cross), MP_ROM_PTR(&v_cross_obj) },
    { MP_ROM_QSTR(MP_QSTR_v_ndc_to_screen), MP_ROM_PTR(&v_ndc_to_screen_obj) },
    { MP_ROM_QSTR(MP_QSTR_m_multiply), MP_ROM_PTR(&m_multiply_obj) },
    { MP_ROM_QSTR(MP_QSTR_m_translate), MP_ROM_PTR(&m_translate_obj) },
    { MP_ROM_QSTR(MP_QSTR_m_rotate), MP_ROM_PTR(&m_rotate_obj) },
    { MP_ROM_QSTR(MP_QSTR_q_rotate), MP_ROM_PTR(&q_rotate_obj) },
};
STATIC MP_DEFINE_CONST_DICT(tidal3d_module_globals, tidal3d_module_globals_table);

const mp_obj_module_t tidal3d_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&tidal3d_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_tidal3d, tidal3d_module);
#endif
