#ifndef __HWACC_CGRA_MAPPER_HH__
#define __HWACC_CGRA_MAPPER_HH__
#include "params/CGRAMapper.hh"
#include "hwacc/compute_unit.hh"

class CGRAMapper : public ComputeUnit {
  private:
  protected:
  public:
    CGRAMapper(CGRAMapperParams *p);
    void tick();
    void initialize();
};

#endif //__HWACC_CGRA_MAPPER_HH__
